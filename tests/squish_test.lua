-- Run from the project root with Lua 5.1 or LuaJIT.
local squish = require("logic.module.squish")

local function near(a, b, epsilon)
    assert(math.abs(a - b) < epsilon, tostring(a) .. " differs from " .. tostring(b))
end

local function response(speed, dt)
    local state = squish.new()
    squish.contact(state, "fruit", 0, 1, speed)
    local peak, minimum = 0, 0
    for _ = 1, math.ceil(1.5 / dt) do
        squish.update(state, dt)
        peak = math.max(peak, state.amount)
        minimum = math.min(minimum, state.amount)
        local normal, tangent = squish.scales(state)
        near(normal * tangent, 1, 1e-12)
        assert(state.amount <= squish.MAX_COMPRESSION)
        assert(state.amount >= -squish.MAX_REBOUND)
    end
    return state, peak, minimum
end

for _, dt in ipairs({1/30, 1/60, 1/120}) do
    local state, peak, minimum = response(1100, dt)
    assert(peak > 0.17, "Hard impact must visibly compress")
    assert(minimum < -0.03, "Impact must visibly rebound")
    assert(state.amount == 0 and state.velocity == 0, "Fruit must settle")
end

local _, gentle = response(260, 1/120)
local _, hard = response(900, 1/120)
assert(hard > gentle * 3, "Harder impact must produce more deformation")

local quiet = squish.new()
for _ = 1, 120 do
    squish.contact(quiet, "floor", 0, 1, 100)
    squish.update(quiet, 1/60)
end
assert(quiet.amount == 0, "Resting contact should stay still")

local resting = squish.new()
squish.contact(resting, "floor", 0, 1, 1000)
for _ = 1, 120 do
    squish.update(resting, 1/60)
    -- Even a large persistent support impulse must not restart the animation.
    squish.contact(resting, "floor", 0, 1, 1000)
end
assert(resting.amount == 0, "Persistent contacts must not retrigger")
for _ = 1, 12 do squish.update(resting, 1/60) end
squish.contact(resting, "floor", 0, 1, 1000)
squish.update(resting, 1/60)
assert(resting.amount > 0, "A later fresh impact should retrigger")

local diagonal = squish.new()
squish.contact(diagonal, "weak", 0, 1, 300)
squish.contact(diagonal, "strong", 1, 1, 1000)
squish.update(diagonal, 1/60)
near(diagonal.nx, math.sqrt(0.5), 1e-12)
near(diagonal.ny, math.sqrt(0.5), 1e-12)
assert(diagonal.amount > 0, "Diagonal impacts must not cancel out")
squish.update(diagonal, 0.7)
assert(diagonal.amount == diagonal.amount and math.abs(diagonal.amount) < 0.01,
       "A slow frame must remain stable")

print("PASS: impact strength, directional response, rebound, settling, area preservation,")
print("      duplicate/resting contacts, re-impact, 30/60/120 FPS and slow-frame stability")
