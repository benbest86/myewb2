"""myEWB credit card helper functions

Most of this code comes from the good people at
http://www.djangosnippets.org/snippets/764/

This file is part of myEWB
Copyright 2009 Engineers Without Borders (Canada) Organisation and/or volunteer contributors

Created on: 2009-08-11
Last modified: 2009-08-12
@author: Francis Kung
"""

import datetime, re, array
        
def ValidateLuhnChecksum(number_as_string):
    """ checks to make sure that the card passes a luhn mod-10 checksum """

    sum = 0
    num_digits = len(number_as_string)
    oddeven = num_digits & 1

    for i in range(0, num_digits):
        digit = int(number_as_string[i])

        if not (( i & 1 ) ^ oddeven ):
            digit = digit * 2
        if digit > 9:
            digit = digit - 9

        sum = sum + digit
        
    return ( (sum % 10) == 0 )

# Regex for valid card numbers
CC_PATTERNS = {
    'MC':'^5[1-5][0-9]{14}$',
    'VI':'^4[0-9]{12}(?:[0-9]{3})?$',
    'AM':'^3[47][0-9]{13}$',
#    'DSC':'^6(?:011|5[0-9]{2})[0-9]{12}$',
}

def ValidateCharacters(number):
    """ Checks to make sure string only contains valid characters """
    return re.compile('^[0-9 ]*$').match(number) != None
        
def StripToNumbers(number):
    """ remove spaces from the number """
    if ValidateCharacters(number):
        result = ''
        rx = re.compile('^[0-9]$')
        for d in number:
            if rx.match(d):
                result += d
        return result
    else:
        raise Exception('Number has invalid digits')

def ValidateDigits(type, number):
    """ Checks to make sure that the Digits match the CC pattern """
    regex = CC_PATTERNS.get(type.upper(), False)
    if regex:
        return re.compile(regex).match(number) != None
    else:
        return False

def ValidateCreditCard(type, number):
    """ Check that a credit card number matches the type and validates the Luhn Checksum """
    type = type.strip().upper()
    if ValidateCharacters(number):
        number = StripToNumbers(number)
        if CC_PATTERNS.has_key(type):
            return ValidateDigits(type, number) and ValidateLuhnChecksum(number)
    return False
