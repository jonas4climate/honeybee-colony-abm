`Bee.py` : Bee class
`BeeHive.py` : Hive entity


# Leafcutter Ants

## Entities

1. `Fungus`. Stationary resource (non-spatial) - state variables:
    1. `Fungal biomass`. Float value - assumed to be the driver behind population growth (as larvae eat it).
        - *Increases* by being fed leaves.
        - *Decreases* by natural decay or consumption.
    2. `Life status`. Boolean state - `true` if alive, `false` if dead.
2. `Ants`. 