local M = {}

local balls = {}

function M.contains(ball)
    for _,id in ipairs(balls) do if id==ball then return true end end
    return false
end

function M.add_ball(ball)
    if M.contains(ball) then return end
    table.insert(balls, ball)
end

function M.remove_ball(ball)
    for i = #balls, 1, -1 do
        if balls[i] == ball then
            table.remove(balls, i)
            break
        end
    end
end

function M.get()
    return balls
end

function M.reset()
    balls = {}
end

return M
