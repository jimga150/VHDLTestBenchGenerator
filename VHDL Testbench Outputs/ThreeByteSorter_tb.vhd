----------------------------------------------------------------------------------
-- Company: 
-- Engineer: 
-- 
-- Create Date: 04/27/2021 17:31:12
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

entity ThreeByteSorter_tb is
end ThreeByteSorter_tb;

architecture Behavioral of ThreeByteSorter_tb is
	
	--General inputs
	signal data1 : STD_LOGIC_VECTOR(7 downto 0) := x"DE";
	signal data2 : STD_LOGIC_VECTOR(7 downto 0) := x"DE";
	signal data3 : STD_LOGIC_VECTOR(7 downto 0) := x"DE";
	
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
		
		-- Not strictly necessary, but prevents process from looping 
		-- if the above assert statement is removed
		wait;
		
	end process;

end Behavioral;
