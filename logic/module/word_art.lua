local M={"Juicilicious!","So juicy!","Dripping!","Moist!",
    "Juice happens!","Thicc & juicy!","Squeeze me!","Oh my pulp!",
    "Certified moist!","Pulp fiction!","Big rind energy!","Peach, please!",
    "Hot fruit mess!","Wet & wild!","Absolutely squelchy!","Fruit around & find out!",
    "Squeeze me harder!","Nice melons!","Sweet & sticky!","Ripe little tease!",
    "Peach got back!","Too ripe to behave!","Forbidden fruit!","Feeling fruity?",
    "Juice all over!","Soft, ripe & ready!","That juicy jiggle!","Oh, that hits the spot!",
    "Double the pleasure!","You make me melt!","Can't keep it in!","One hot squeeze!"}
local last=0
function M.next()
    local pick=last==0 and math.random(1,#M) or math.random(1,#M-1)
    if last>0 and pick>=last then pick=pick+1 end
    last=pick;return M[pick]
end
return M
