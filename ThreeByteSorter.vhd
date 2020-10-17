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
    Port ( data1, data2, data3 : in STD_LOGIC_VECTOR (7 downto 0);
           high, med, low : out STD_LOGIC_VECTOR (7 downto 0));
end ThreeByteSorter;

architecture Structural of ThreeByteSorter is

    signal low_23, high_23, high_low23_1 : std_logic_vector(7 downto 0);

begin

    sorter_23 : entity work.Sorter
    port map(
        data1 => data2,
        data2 => data3,
        high => high_23,
        low => low_23
    );
    
    sorter_1 : entity work.Sorter
    port map(
        data1 => data1,
        data2 => low_23,
        high => high_low23_1,
        low => low
    );
    
    sorter_final : entity work.Sorter
    port map(
        data1 => high_23,
        data2 => high_low23_1,
        high => high,
        low => med
    );


end Structural;
