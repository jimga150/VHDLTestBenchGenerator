----------------------------------------------------------------------------------
-- Company: 
-- Engineer: 
-- 
-- Create Date: 04/27/2021 16:55:22
-- Design Name: MLUART_RX_tb
-- Module Name: MLUART_RX_tb - Behavioral
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
use IEEE.STD_LOGIC_UNSIGNED.ALL;

entity MLUART_RX_tb is
end MLUART_RX_tb;

architecture Behavioral of MLUART_RX_tb is
    
    --Clocks
    signal CLK_100MHZ : std_logic := '0';
    signal clk_en_16_x_baud : std_logic := '0';
    
    --General inputs
    signal UART_RX : std_logic := '0';
    
    --Outputs
    signal read_data_complete : std_logic;
    signal data_out : std_logic_vector(7 downto 0);
    
    --Clock Periods
    constant CLK_100MHZ_period : time := 10 ns;
    constant clk_en_16_x_baud_period : time := 10 ns;
    
begin
    
    UUT: entity work.MLUART_RX
    port map(
        CLK_100MHZ => CLK_100MHZ,
        clk_en_16_x_baud => clk_en_16_x_baud,
        read_data_complete => read_data_complete,
        data_out => data_out,
        UART_RX => UART_RX
    );
    
    --Clock Drivers
    CLK_100MHZ <= not CLK_100MHZ after CLK_100MHZ_period/2;
    clk_en_16_x_baud <= not clk_en_16_x_baud after clk_en_16_x_baud_period/2;
    
    stim_proc: process is begin
        
        wait for CLK_100MHZ_period;
        
        --Insert stimuli here
        
        assert false report "End Simulation" severity failure;
        
        -- Not strictly necessary, but prevents process from looping 
        -- if the above assert statement is removed
        wait;
        
    end process;

end Behavioral;
