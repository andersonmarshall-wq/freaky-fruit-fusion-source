local M = {}

local savefile = sys.get_save_file("freaky_fruit_fusion", "savefile")
--sys.save(savefile, { check = true })
local saved_data = sys.load(savefile)

function M.load()
    saved_data = sys.load(savefile)
    return saved_data
end

function M.save(key, value)
    M.load()
    saved_data[key] = value
    sys.save(savefile, saved_data)
end

return M
