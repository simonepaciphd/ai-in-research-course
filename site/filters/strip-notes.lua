-- Keep public HTML free of presenter notes and author comments.
function Div(el)
  if el.classes:includes("notes") then
    return {}
  end
end

function RawBlock(el)
  if el.format == "html" and el.text:match("^%s*<!%-%-") then
    return {}
  end
end
