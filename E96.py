#region imports
import bisect
import math
#endregion

#region constants
# Values in the E96 series of resistors
# naming convention:  capital letters for constants, lower case for variables
E96_VALUES = (100,102,105,107,110,113,115,118,121,124,127,130,133,137,140,143,147,150,
       154,158,162,165,169,174,178,182,187,191,196,200,205,210,215,221,226,232,
       237,243,249,255,261,267,274,280,287,294,301,309,316,324,332,340,348,357,
       365,374,383,392,402,412,422,432,442,453,464,475,487,499,511,523,536,549,
       562,576,590,604,619,634,649,665,681,698,715,732,750,768,787,806,825,845,
       866,887,909,931,953,976,1000)
#endregion

#region functions
def getClosestE96(value):
    """
    Returns the closest E96 resistor value to the given value along with the multiplier used to normalize it.
    :param value: The target resistor value.
    :return: A tuple containing the closest E96 resistor value and the multiplier used to normalize the value.
    """
    try:
        # Normalize the value to the E96 range (100-1000)
        multiplyer, base_value = getMultiplier(value)

        #use bisect to find the indices of the closest values in the E96 series
        closest_indices = [bisect.bisect_left(E96_VALUES, base_value), bisect.bisect_right(E96_VALUES, base_value)]
        left_diff = abs(E96_VALUES[closest_indices[0]] - base_value)
        right_diff = abs(E96_VALUES[closest_indices[1]] - base_value)
        closest_value = E96_VALUES[closest_indices[0]] if left_diff <= right_diff else E96_VALUES[closest_indices[1]]
        # Return the closest E96 value multiplied by the original multiplier
        return (closest_value * multiplyer, multiplyer)
    except ValueError as e:
        print(f"Error in getClosestE96: {e}")
        return (0, 1)

def getMultiplier(value):
    """
    Returns the multiplier needed to normalize the given value to the E96 range (100-1000).
    May raise a ValueError if the value is zero or negative.
    :param value: The target resistor value.
    :return: The multiplier and the normalized base value as a tuple.
    """
    multiplyer = 1
    base_value = value
    if base_value <= 0.0:
         raise ValueError("Value cannot be zero or negative.")
    while base_value > 1000:
        base_value /= 10
        multiplyer *= 10
    while base_value < 100:
        base_value *= 10
        multiplyer /= 10
    return (multiplyer,base_value)

def getColors(value):
    """
    Returns the color bands for a given resistor value.
    :param value: The target resistor value.
    :return: A list of color bands corresponding to the resistor value.
    """
    # Define the color codes for digits and multipliers
    colors = ["black", "brown", "red", "orange", "yellow", "green", "blue", "violet", "gray", "white"]
    closest_value, multiplier = getClosestE96(value)
    base_value = int(closest_value / multiplier)
    digits = [int(d) for d in str(base_value)]
    color_bands = [colors[d] for d in digits]
    # Add the multiplier color
    multiplier_index = int(round(math.log10(multiplier)))
    color_bands.append(colors[multiplier_index])
    return color_bands

def main():
    """_summary_
        Entry point for the program. 
        Prompts the user for resistor values and displays the closest E96 value
        and its color bands.
    Raises:
        ValueError: _description_
    """
    GoAgain = True
    while GoAgain:
       try:
              value = float(input("Enter the resistor value: "))
              if value < 1 or value > 10e6:
                     raise ValueError("Value out of range.")
              closest_value = getClosestE96(value)[0]
              color_bands = getColors(closest_value)
              print("Closest E96 value:", closest_value)
              print("Color bands:", color_bands)
       except ValueError:
              print("Invalid input. Please enter a numeric value between 1 and 10M.  Acceptable suffixes are k and M")
       finally:
              GoAgain = input("Do you want to enter another value? (y/n): ").strip().lower() == "y"
#endregion

if __name__ == "__main__":
    main()