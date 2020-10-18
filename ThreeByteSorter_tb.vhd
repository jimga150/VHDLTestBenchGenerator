----------------------------------------------------------------------------------
-- Company: 
-- Engineer: 
-- 
-- Create Date: 10/18/2020 12:10:24
-- Design Name: ThreeByteSorter_tb
-- Module Name: ThreeByteSorter_tb - Behavioral
-- Project Name: 
-- Target Devices: 
-- Tool Versions: 
-- Description: 
-- 
-- Dependencies: 
-- 
-- Revision:
-- Revision 0.01 - File Created
-- Additional Comments: Created with VHDL Test Bench Template Generator
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

entity ThreeByteSorter_tb is
end ThreeByteSorter_tb;

architecture Behavioral of ThreeByteSorter_tb is
    
    --General inputs
    signal data1 : STD_LOGIC_VECTOR(7 downto 0) := (others => '0');
    signal data2 : STD_LOGIC_VECTOR(7 downto 0) := (others => '0');
    signal data3 : STD_LOGIC_VECTOR(7 downto 0) := (others => '0');
    
    --Outputs
    signal high : STD_LOGIC_VECTOR(7 downto 0);
    signal med : STD_LOGIC_VECTOR(7 downto 0);
    signal low : STD_LOGIC_VECTOR(7 downto 0);
    
begin
    
    UUT: entity work.ThreeByteSorter
    port map(
        data1 => data1,
        data2 => data2,
        data3 => data3,
        high => high,
        med => med,
        low => low
    );
    
    
    stim_proc: process is begin
        
        --Insert stimuli here
        
        assert false report "End Simulation" severity failure;
        
    end process;

end Behavioral;
