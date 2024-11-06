module mod_example
    !> mod_example docstrings
    !> still some documentation
    !>
    !> yet more lines
    !> \( ax^2 + bx + c = 0 \)
    implicit none
    private
    
    type, public :: my_type
        !> my_type docstrings
        integer :: a = 1
        real, allocatable :: x(:)
    end type

contains

elemental subroutine my_sub(x,y)
!> mysub docstrings
!> \[
!> x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}
!> \]
    real, intent(in) :: x !> input variable
    real, intent(inout) :: y !> output variable
end subroutine
    
end module mod_example