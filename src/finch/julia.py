import juliapkg
#To change the version of Finch used, see the documentation for pyjuliapkg here: https://github.com/JuliaPy/pyjuliapkg
#Use pyjuliapkg to modify the `juliapkg.json` file in the root of this repo.
#You can also run `develop.py` to quickly use a local copy of Finch.jl.
#An example development json is found in `juliapkg_dev.json`
import juliacall as jc  # noqa

juliapkg.resolve()

from juliacall import Main as jl  # noqa

jl.seval("using Finch")
jl.seval("using HDF5")
jl.seval("using NPZ")
jl.seval("using TensorMarket")
jl.seval("using Random")
jl.seval("using Statistics")
