from django import template

register = template.Library()

@register.filter
def to_fraction(value):

    common_fractions = {
        0.25: '1/4',
        0.5: '1/2',
        0.75: '3/4',
        0.333: '1/3',
        0.667: '2/3',
        0.125: '1/8',
    }
    
    rounded = round(float(value), 3)

    if rounded in common_fractions:
        return common_fractions[rounded]
    
    if rounded.is_integer():
        return int(rounded)
    
    return f'{float(value):g}'


@register.filter
def time_converter(value):

    if value > 60:
        hrs = value // 60
        mins = value % 60

        if hrs > 24:
            days = hrs // 24
            hrs = hrs % 24

            if hrs > 0:
                if mins > 0:
                    return f"{days} Tage {hrs} Std. {mins} Min."
                else:
                    return f"{days} Tage {hrs} Std."
            else:
                return f"{days} Tage"
                
        
        else:
            if mins > 0:
                return f"{hrs} Std. {mins} Min."
            else:
                return f"{hrs} Std."
    
    else:
        return f"{value} Min."
    
    
@register.filter
def multiply(value, arg):
    return float(value) * float(arg)