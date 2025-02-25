module mod_example
    !! mod_example docstrings
    !! still some documentation
    !!
    !! yet more lines
    !! \( ax^2 + bx + c = 0 \)
    implicit none
    private
    
    type, public :: my_type
        !! my_type docstrings
        integer :: a = 1
        real, allocatable :: x(:)
    end type

contains

pure elemental function f1(x)result(r)
    !! f1 docstring.
    real, intent(in) :: x !! arg for f1
    real :: r
end function

real function f2(x, y)
    !! f2 dosctring.
    !! Test with one optional argument.
    real, intent(in) :: x          !! arg for f2
    real, intent(in), optional ::y !! Optional arg
end function

elemental subroutine my_sub(x,y)
!! mysub docstrings
!! 
!! \[
!! x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}
!! \]
    real, intent(in) :: x !! input variable
    real, intent(inout) :: y !! output variable
end subroutine
    
end module mod_example