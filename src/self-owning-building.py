from pyteal import *

def self_owning_building():
    # Define app global state
    owner = Bytes("owner")
    price = Int("price")
    rent = Int("rent")
    maintenance_cost = Int("maintenanceCost")
    last_rent_payment = Int("lastRentPayment")
    last_maintenance_payment = Int("lastMaintenancePayment")
    penalty_fee = Int("penaltyFee")

    # Check if the app is being created
    on_creation = Txn.type_enum() == TxnType.ApplicationCall and Txn.application_id() == Int(0)

    # Define the contract for app creation
    on_creation_branch = Seq([
        App.globalPut(owner, Txn.sender()),
        App.globalPut(price, Int(1000000)),  # example values, these can be adjusted
        App.globalPut(rent, Int(10000)),
        App.globalPut(maintenance_cost, Int(5000)),
        App.globalPut(penalty_fee, Int(2000)),
        App.globalPut(last_rent_payment, Global.latest_timestamp()),
        App.globalPut(last_maintenance_payment, Global.latest_timestamp()),
        Return(Int(1))
    ])

    # Define the contract for payment of rent
    pay_rent_branch = Seq([
        Assert(Txn.type_enum() == TxnType.Payment),
        Assert(Txn.amount() >= App.globalGet(rent)),
        App.globalPut(last_rent_payment, Global.latest_timestamp()),
        Return(Int(1))
    ])

    # Define the contract for payment of maintenance
    pay_maintenance_branch = Seq([
        Assert(Txn.type_enum() == TxnType.Payment),
        Assert(Txn.amount() >= App.globalGet(maintenance_cost)),
        App.globalPut(last_maintenance_payment, Global.latest_timestamp()),
        Return(Int(1))
    ])

    # Logic to define the main branch of the contract
    main_branch = Cond(
        [on_creation, on_creation_branch],
        [Txn.application_args[0] == Bytes("pay_rent"), pay_rent_branch],
        [Txn.application_args[0] == Bytes("pay_maintenance"), pay_maintenance_branch]
    )

    return main_branch

print(compileTeal(self_owning_building(), Mode.Application))
