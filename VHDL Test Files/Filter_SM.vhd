----------------------------------------------------------------------------------
-- Company: 
-- Engineer: 
-- 
-- Create Date: 04/15/2020 04:52:37 PM
-- Design Name: 
-- Module Name: Filter_SM - Behavioral
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
use IEEE.NUMERIC_STD.ALL;

-- Uncomment the following library declaration if instantiating
-- any Xilinx leaf cells in this code.
--library UNISIM;
--use UNISIM.VComponents.all;

entity Filter_SM is
    generic(
        depth_of_pipeline:integer:=4; -- offset used when writing to write address
        test_generic : unsigned(3 downto 0) := "0100";
        foobar : std_ulogic_vector(0 to 27) := (others => '0');
        test_int :integer:=5
    );
    port(
        clk, rst : in std_logic;
        
        set_ba_write, set_ba_read : in std_logic;
        start : in std_logic;
        numpixels_in : in std_logic_vector(31 downto 0);
        num_cols_in : in std_logic_vector(0 to test_int - 1);
        sl_sm_done : in std_logic;
        num_thingys : in integer := test_int + to_integer(test_generic);
        
        en1, en2 : out std_logic;
        addr, numpixels_out : out std_logic_vector(test_int-1 downto 0);
        start_write_out, write_en, start_read : out std_logic;
        done : out std_logic
    );
end Filter_SM;

architecture Behavioral of Filter_SM is

    type state_type is (
        --Removed
    );
    
    signal filter_state, filter_nextstate : state_type := IDLE;
    
    constant write_base_address : std_logic_vector(31 downto 0) := x"00040000"; --remember that the top 5 bits of this are not used
    constant corrected_write_base_address : std_logic_vector(31 downto 0) := 
        std_logic_vector(unsigned(write_base_address) - to_unsigned(depth_of_pipeline, 32));
    constant read_base_address : std_logic_vector(31 downto 0) := x"00000000";
    
    signal addr_offset : std_logic_vector(31 downto 0) := (others => '0');
    
    signal num_cols_padded : std_logic_vector(31 downto 0);
    
    signal base_address, current_center_address, curr_col_offset, net_address, end_address : std_logic_vector(31 downto 0);
    
    signal base_addr_sel : std_logic;

begin

    sync_proc: process(clk) is begin
        if rising_edge(clk) then
            if rst = '1' then
                filter_state <= IDLE;
                addr_offset <= (others => '0');
            else
            

                
                filter_state <= filter_nextstate;
                
            end if;
        end if;
    end process;
    
    nextstate_proc: process(
        filter_state, 
        set_ba_write, set_ba_read, 
        start, 
        numpixels_in, num_cols_in,
        sl_sm_done,
        current_center_address, end_address
    ) is begin
        
        --Removed
        
    end process nextstate_proc;

end Behavioral;
