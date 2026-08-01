import jax
import jax.numpy as jnp
import numpy as np
import os
from jax_fem.problem import Problem
from jax_fem.solver import solver, ad_wrapper
from jax_fem.generate_mesh import box_mesh_gmsh, Mesh
from jax_fem.utils import save_sol

class DifferentiableTree(Problem):
    def set_params(self, params):
        # params[0] is radius
        radius = params[0]
        quad_pts = self.fes[0].get_physical_quad_points()
        dists = jnp.sqrt(quad_pts[..., 0]**2 + quad_pts[..., 2]**2)
        beta, E_wood, E_air = 2.0, 10000.0, 1.0
        rho = jax.nn.sigmoid(beta * (radius - dists))
        self.internal_vars = (E_air + (E_wood - E_air) * rho,)

    def get_universal_kernel(self):
        def stress(u_grad, E):
            nu = 0.3
            mu = E / (2. * (1. + nu))
            lmbda = E * nu / ((1 + nu) * (1 - 2 * nu))
            epsilon = 0.5 * (u_grad + u_grad.T)
            return lmbda * jnp.trace(epsilon) * jnp.eye(self.dim) + 2 * mu * epsilon

        def universal_kernel(cell_sol_flat, x, cell_shape_grads, cell_JxW, cell_v_grads_JxW, *cell_internal_vars):
            cell_sol_list = self.unflatten_fn_dof(cell_sol_flat)
            cell_sol = cell_sol_list[0]
            num_nodes = self.fes[0].num_nodes
            cell_shape_grads = cell_shape_grads[:, :num_nodes, :]
            cell_v_grads_JxW = cell_v_grads_JxW[:, :num_nodes, :, :]
            design_E = cell_internal_vars[0]
            u_grads = cell_sol[None, :, :, None] * cell_shape_grads[:, :, None, :]
            u_grads = jnp.sum(u_grads, axis=1)
            u_physics = jax.vmap(stress)(u_grads, design_E)
            val = jnp.sum(u_physics[:, None, :, :] * cell_v_grads_JxW, axis=(0, -1))
            return jax.flatten_util.ravel_pytree(val)[0]
        return universal_kernel

def setup_optimization():
    data_dir = "output/opt"
    os.makedirs(data_dir, exist_ok=True)
    nx, ny, nz = 6, 12, 6 # Smaller mesh for faster JIT
    lx, ly, lz = 40.0, 80.0, 40.0
    meshio_mesh = box_mesh_gmsh(nx, ny, nz, lx, ly, lz, data_dir, ele_type='HEX8')
    meshio_mesh.points[:, 0] -= lx/2
    meshio_mesh.points[:, 2] -= lz/2
    mesh = Mesh(meshio_mesh.points, meshio_mesh.cells_dict['hexahedron'])
    min_y = 0.0
    def base(point): return jnp.isclose(point[1], min_y, atol=1e-3)
    def zero_val(point): return 0.
    dirichlet_bc_info = [[base, base, base], [0, 1, 2], [zero_val, zero_val, zero_val]]
    problem = DifferentiableTree(mesh, vec=3, dim=3, ele_type='HEX8', dirichlet_bc_info=dirichlet_bc_info)
    return problem, mesh

def run_optimization():
    problem, mesh = setup_optimization()
    fwd_solver = ad_wrapper(problem)
    
    def objective(radius):
        sol_list = fwd_solver(jnp.array([radius]))
        max_y = jnp.max(mesh.points[:, 1])
        top_mask = jnp.isclose(mesh.points[:, 1], max_y, atol=1e-3)
        top_disp = sol_list[0][top_mask, 0]
        # Loss: minimize compliance + material cost
        return jnp.sum(top_disp**2) + 0.01 * radius**2

    grad_fn = jax.grad(objective)
    r = 10.0
    print(f"Initial Radius: {r} mm")
    print("\nStarting Optimization Cycle...")
    for i in range(5):
        loss = objective(r)
        g = grad_fn(r)
        # Update radius
        r = jnp.clip(r - 10.0 * g, 5.0, 20.0)
        print(f"Step {i+1}: Radius = {r:.4f} mm, Loss = {loss:.6f}, Grad = {g:.6f}")
    print(f"\nOptimization complete. Final Recommended Radius: {r:.2f} mm")

if __name__ == "__main__":
    from jax import config
    config.update("jax_enable_x64", True)
    run_optimization()
