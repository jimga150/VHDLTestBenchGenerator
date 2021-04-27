----------------------------------------------------------------------------------
-- Company: 
-- Engineer: 
-- 
-- Create Date: 04/27/2021 17:31:43
-- Design Name: Filter_SM_tb
-- Module Name: Filter_SM_tb - Behavioral
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
use IEEE.NUMERIC_STD.ALL;

entity Filter_SM_tb is
end Filter_SM_tb;

architecture Behavioral of Filter_SM_tb is
	
	--Generics
	constant depth_of_pipeline : integer := 4;
	constant test_generic : unsigned(3 downto 0) := "0100";
	constant foobar : std_ulogic_vector(0 to 27) := (others => '0');
	constant test_int : integer := 5;
	
	
	--Clocks
	signal clk : std_logic := '0';
	signal clok : std_logic := '0';
	
	--Resets
	signal rst : std_logic := '1';
	signal rastn : std_logic := '0';
	
	--General inputs
	signal set_ba_write : std_logic := '0';
	signal set_ba_read : std_logic := '0';
	signal start : std_logic := '0';
	signal numpixels_in : std_logic_vector(31 downto 0) := (others => '0');
	signal num_cols_in : std_logic_vector(0 to test_int - 1) := (others => '0');
	signal sl_sm_done : std_logic := '0';
	signal num_thingys : integer := test_int + to_integer(test_generic);
	
	--Outputs
	signal en1 : std_logic;
	signal en2 : std_logic;
	signal addr : std_logic_vector(test_int-1 downto 0);
	signal numpixels_out : std_logic_vector(test_int-1 downto 0);
	signal start_write_out : std_logic;
	signal write_en : std_logic;
	signal start_read : std_logic;
	signal done : std_logic;
	
	--Clock Periods
	constant clk_period : time := 10 ns;
	constant clok_period : time := 10 ns;
	
begin
	
	UUT: entity work.Filter_SM
	generic map(
		depth_of_pipeline => depth_of_pipeline,
		test_generic => test_generic,
		foobar => foobar,
		test_int => test_int
	)
	port map(
		clk => clk,
		clok => clok,
		rst => rst,
		rastn => rastn,
		set_ba_write => set_ba_write,
		set_ba_read => set_ba_read,
		start => start,
		numpixels_in => numpixels_in,
		num_cols_in => num_cols_in,
		sl_sm_done => sl_sm_done,
		num_thingys => num_thingys,
		en1 => en1,
		en2 => en2,
		addr => addr,
		numpixels_out => numpixels_out,
		start_write_out => start_write_out,
		write_en => write_en,
		start_read => start_read,
		done => done
	);
	
	--Clock Drivers
	clk <= not clk after clk_period/2;
	clok <= not clok after clok_period/2;
	
	stim_proc: process is begin
		
		wait for clk_period;
		
		rst <= '0';
		rastn <= '1';
		
		wait for clk_period;
		
		--Insert stimuli here
		
		assert false report "End Simulation" severity failure;
		
		-- Not strictly necessary, but prevents process from looping 
		-- if the above assert statement is removed
		wait;
		
	end process;

end Behavioral;
