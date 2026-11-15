local quote_index = -1
local decisions = {}
local images = {}

local function load_runtime()
  local path = os.getenv("MD2TYPST_RUNTIME")
  if not path then
    return
  end
  local file = assert(io.open(path, "r"))
  local content = file:read("*a")
  file:close()
  local runtime = pandoc.json.decode(content)
  decisions = runtime.quotes or {}
  images = runtime.images or {}
end

local function render_callout(blocks, kind)
  local body = pandoc.write(pandoc.Pandoc(blocks), "typst")
  return pandoc.RawBlock(
    "typst",
    '#callout("' .. kind .. '")[\n' .. body .. ']\n'
  )
end

local explicit_kinds = {
  NOTE = "note",
  TIP = "tip",
  IMPORTANT = "warning",
  WARNING = "warning",
  CAUTION = "warning"
}

local function rewrite_image(element)
  local target = images[element.src]
  if target then
    element.src = target
    return element
  end
end

local function render_quote(element)
  quote_index = quote_index + 1
  local first = element.content[1]
  if first and (first.t == "Para" or first.t == "Plain") then
    local marker = first.content[1]
    if marker and marker.t == "Str" then
      local label = marker.text:match("^%[!([A-Za-z]+)%]$")
      local kind = label and explicit_kinds[label:upper()]
      if kind then
        table.remove(first.content, 1)
        if first.content[1] and first.content[1].t == "SoftBreak" then
          table.remove(first.content, 1)
        end
        if #first.content == 0 then
          table.remove(element.content, 1)
        end
        return render_callout(element.content, kind)
      end
    end
  end

  local decision = decisions[tostring(quote_index)]
  if decision and decision.action == "callout" then
    return render_callout(element.content, decision.kind)
  end
end

load_runtime()

return {
  {
    traverse = "bottomup",
    Image = rewrite_image,
    BlockQuote = render_quote
  }
}
