import unittest
import os
from fspx.fortran_parser_ford import parse_fortran_file

class TestFortranAutodoc(unittest.TestCase):

    def test_basic_parsing(self):
        fortran_code = '''
module math_utils
  !> This module provides utilities for mathematical operations
  implicit none

  contains

  subroutine add_integers(a, b, c)
    !> Adds two integers and returns the result
    !> but the comment continues in the next line
    integer, intent(in) :: a   !> The first integer to add
    integer, intent(in) :: b   !> The second integer to add
    integer, intent(out) :: c  !> The result of the addition
    c = a + b
  end subroutine add_integers

  elemental function multiply_reals(x, y) result(res)
    !> Multiplies two real numbers and returns the result
    real, intent(in) :: x   !> The first real number to multiply
    real, intent(in) :: y   !> The second real number to multiply
    real :: res  !> The result of the multiplication
    res = x * y
  end function multiply_reals
end module math_utils'''
        with open('test.f90', 'w') as f:
            f.write(fortran_code)
        
        parsed_data = parse_fortran_file('test.f90')
        os.remove('test.f90')
        self.assertIn('modules', parsed_data)
        self.assertEqual(parsed_data['modules'][0]['name'], 'math_utils')
        self.assertEqual(parsed_data['modules'][0]['doc'], ' This module provides utilities for mathematical operations')
        self.assertEqual(parsed_data['subroutines'][0]['name'], 'add_integers')
        self.assertEqual(parsed_data['subroutines'][0]['doc'], ' Adds two integers and returns the result but the comment continues in the next line')
        self.assertEqual(parsed_data['functions'][0]['name'], 'multiply_reals')
        self.assertEqual(parsed_data['functions'][0]['doc'], ' Multiplies two real numbers and returns the result')
        self.assertEqual(parsed_data['functions'][0]['attributes'], 'elemental')

if __name__ == '__main__':
    unittest.main()