import paystack

ctx=paystack.Paystack()

"""
initialize transaction

"""
print(ctx.initialize_transaction("ovedheo@gmail.com",200))



"""

confirm transaction

"""
# print(ctx.confirm_transaction("tjkdiy1rg1i7esh"))