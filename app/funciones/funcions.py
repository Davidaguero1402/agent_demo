def calculate(what):
    return eval(what)

def average_dog_weight(name):
    if name in "Scottish Terrier": 
        return("Scottish Terriers average 20 lbs")
    elif name in "Border Collie":
        return("a Border Collies average weight is 37 lbs")
    elif name in "Toy Poodle":
        return("a toy poodles average weight is 7 lbs")
    else:
        return("An average dog weights 50 lbs")
    
def what_is_his_weight(name):
    if name == "David":  # Usa una comparación directa
        return "His weight: 70kgs"
    else:
        return f"I don't know the weight of {name}"
