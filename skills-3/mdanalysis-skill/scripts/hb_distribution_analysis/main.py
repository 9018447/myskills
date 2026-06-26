#!/usr/bin/env python3
"""Main CLI entry point for the generic hydrogen-bond analysis package."""

import argparse
import sys


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="通用氢键分析工具（支持任意分子体系，通过 YAML 配置）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 内置 ChCl:EG 配置，分析最后 50 帧
  python -m scripts.hb_distribution_analysis -t md.tpr -r md.xtc -n 50

  # 自定义体系 YAML
  python -m scripts.hb_distribution_analysis -t md.tpr -r md.xtc -c my_system.yaml -n 100

  # 全轨迹分析，自定义截断参数
  python -m scripts.hb_distribution_analysis -t md.tpr -r md.xtc -d 3.2 -a 130
        """,
    )

    # 必需参数
    parser.add_argument(
        "-t", "--topology", required=True, help="拓扑文件路径（.tpr、.gro、.pdb 等）"
    )
    parser.add_argument(
        "-r", "--trajectory", required=True, help="轨迹文件路径（.xtc、.trr、.dcd 等）"
    )

    # 可选参数
    parser.add_argument(
        "-c",
        "--config",
        default=None,
        help="体系配置 YAML 文件路径 [默认：内置 ChCl:EG 配置]",
    )
    parser.add_argument(
        "-d",
        "--distance",
        type=float,
        default=None,
        help="D-A 截断距离（Å）[覆盖 YAML 设置]",
    )
    parser.add_argument(
        "-a",
        "--angle",
        type=float,
        default=None,
        help="D-H-A 最小角度（°）[覆盖 YAML 设置]",
    )
    parser.add_argument(
        "-n",
        "--last-frames",
        type=int,
        default=None,
        metavar="N",
        help="只分析末尾 N 帧 [默认：全轨迹]",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=None,
        help="输出目录 [默认：由 YAML 的 output_dir 指定]",
    )

    # 标志
    parser.add_argument("--no-plots", action="store_true", help="跳过绘图")
    parser.add_argument("--no-data", action="store_true", help="跳过数据导出")
    parser.add_argument("-v", "--verbose", action="store_true", help="详细输出")

    return parser.parse_args()


def main():
    args = parse_arguments()

    print("Starting Hydrogen Bond Analysis")
    print("=" * 50)

    try:
        from . import (
            HBAnalyzer,
            default_config,
            load_config,
            print_summary,
            run_analysis,
        )
    except ImportError as e:
        print(f"Error importing scripts.hb_distribution_analysis: {e}")
        sys.exit(1)

    try:
        # ── 加载配置
        if args.config:
            print(f"Loading config from: {args.config}")
            config = load_config(args.config)
        else:
            config = default_config()

        # CLI 参数覆盖 YAML 截断值
        config.override_cutoffs(args.distance, args.angle)

        if args.verbose:
            print("\nConfiguration:")
            print(config.summary())
            print(f"  Last frames: {args.last_frames if args.last_frames else 'all'}")

        # ── 确定输出目录（CLI > YAML > 默认）
        output_dir = args.output or config.output_dir

        # ── 初始化分析器
        analyzer = HBAnalyzer(
            args.topology,
            args.trajectory,
            config=config,
        )

        # ── 运行分析
        run_analysis(
            analyzer,
            output_dir=output_dir,
            create_plots=not args.no_plots,
            save_data=not args.no_data,
            last_frames=args.last_frames,
        )

        # ── 打印摘要
        print_summary(analyzer)

        # ── 输出文件列表
        print("\n" + "=" * 50)
        print("OUTPUT FILES")
        print("=" * 50)
        print(f"Directory: {output_dir}/")

        if not args.no_plots:
            print("\nVisualization plots:")
            print(
                "- hb_2d_density_maps.png/pdf   : XY plane hydrogen bond density maps"
            )
            print("- hb_lifetime_autocorr.png/pdf : Lifetime autocorrelation functions")

        if not args.no_data:
            print("\nData files:")
            print("- hb_density_maps.npz  : 2D density arrays (NumPy format)")
            print("- hb_lifetime_data.csv : Lifetime ACF data (CSV format)")

        print("\nAnalysis complete!")

    except FileNotFoundError as e:
        print(f"\nError: File not found: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nError during analysis: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
