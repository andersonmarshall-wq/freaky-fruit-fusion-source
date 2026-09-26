-- Game-feel values inspired by ripe fruit, not a biological simulation.
local M = {
    {name="Cherry",        radius=40,    softness=0.72, bounce=0.22},
    {name="Blueberry",     radius=50,    softness=0.95, bounce=0.20},
    {name="Passion fruit", radius=62.5,  softness=0.40, bounce=0.27},
    {name="Kiwi",          radius=70,    softness=0.64, bounce=0.23},
    {name="Orange",        radius=82.5,  softness=0.46, bounce=0.27},
    {name="Peach",         radius=95,    softness=1.00, bounce=0.18},
    {name="Coconut",       radius=110,   softness=0.16, bounce=0.32},
    {name="Pineapple",     radius=125,   softness=0.28, bounce=0.28},
    {name="Honeydew",      radius=135,   softness=0.25, bounce=0.29},
    {name="Cantaloupe",   radius=150,   softness=0.30, bounce=0.28},
    {name="Watermelon",    radius=165,   softness=0.24, bounce=0.30},
    {name="Golden melon",  radius=165,   softness=0.30, bounce=0.28},
}
function M.get(tier) return M[tier] or M[1] end
return M
