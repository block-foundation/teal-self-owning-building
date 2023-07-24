from pyteal import *

def rent_payment():

    # Get global and local schema
    global_schema = GlobalSchema(num_uints=1, num_byte_slices=0)
    local_schema = LocalSchema(num_uints=2, num_byte_slices=0)

    # Define global and local variables
    g_total_rent = Bytes("total_rent")
    l_last_paid = Bytes("last_paid")
    l_rent_due = Bytes("rent_due")

    # Define program
    program = Seq([
        Cond(
            [Txn.application_id() == Int(0), Seq([App.localPut(Int(0), l_rent_due, Txn.application_args[0]),
                                                  App.localPut(Int(0), l_last_paid, Global.latest_timestamp()),
                                                  App.globalPut(g_total_rent, Add(App.globalGet(g_total_rent), Txn.application_args[0])),
                                                  Return(Int(1))])],

            [And(Txn.application_id() != Int(0), Txn.application_args.length() == Int(0)), Seq([Assert(And(Global.latest_timestamp() > Add(App.localGet(Int(0), l_last_paid), Mul(Int(86400), Int(30))),
                                                                                                 App.localGet(Int(0), l_rent_due) == Int(0))),
                                                                                               App.localPut(Int(0), l_last_paid, Global.latest_timestamp()),
                                                                                               App.globalPut(g_total_rent, Sub(App.globalGet(g_total_rent), App.localGet(Int(0), l_rent_due))),
                                                                                               Return(Int(1))])],

            [And(Txn.application_id() != Int(0), Txn.application_args.length() > Int(0)), Seq([App.localPut(Int(0), l_rent_due, Txn.application_args[0]),
                                                                                               Return(Int(1))])]
        )
    ])

    # Return teal program
    return compileTeal(program, mode=Mode.Application, version=4)

if __name__ == "__main__":
    print(compileTeal(rent_payment(), mode=Mode.Application, version=4))
