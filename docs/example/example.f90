module mod_example
    !> mod_example docstrings
    !> still some documentation
    !>
    !> yet more lines
    implicit none
    private
    
    type, public :: my_type
        !> my_type docstrings
        integer :: a = 1
        real, allocatable :: x(:)
    end type

contains

subroutine my_sub(x,y)
!> mysub docstrings
    real, intent(in) :: x !> input variable
    real, intent(inout) :: y !> output variable
end subroutine
    
end module mod_example