----------------------------------------------------------------------------------
-- Company: 
-- Engineer: 
-- 
-- Create Date: 04/14/2020 10:18:16 AM
-- Design Name: 
-- Module Name: ThreeByteSorter - Structural
-- Project Name: 
-- Target Devices: 
-- Tool Versions: 
-- Description: 
-- 
-- Dependencies: 
-- 
-- Revision:
-- Revision 0.01 - File Created
-- Additional Comments:
-- 
----------------------------------------------------------------------------------


library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

-- Uncomment the following library declaration if using
-- arithmetic functions with Signed or Unsigned values
--use IEEE.NUMERIC_STD.ALL;

-- Uncomment the following library declaration if instantiating
-- any Xilinx leaf cells in this code.
--library UNISIM;
--use UNISIM.VComponents.all;

entity ThreeByteSorter is
    Port ( data1, data2, data3 : in STD_LOGIC_VECTOR (7 downto 0) := x"DE";
           high, med, low : out STD_LOGIC_VECTOR (7 downto 0));
end ThreeByteSorter;

architecture Structural of ThreeByteSorter is

    

begin

    --Removed


end Structural;
