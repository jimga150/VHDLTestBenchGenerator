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
        IDLE, 
        SEND_WRITE_BA, 
        PREP_FILTER, 
        START_CENTER_READ, 
        WAIT_C_READ, 
        START_UPPER_READ,
        WAIT_U_READ,
        START_LOWER_READ,
        WAIT_L_READ,
        PUSH_PIPELINE,
        START_WRITE,
        WAIT_WRITE,
        INCREMENT_OFFSET
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
            
                case filter_state is 
                    when IDLE => addr_offset <= (others => '0');
                    when PREP_FILTER => addr_offset <= num_cols_padded;
                    when INCREMENT_OFFSET => addr_offset <= std_logic_vector(unsigned(addr_offset) + 1);
                    when others => addr_offset <= addr_offset;
                end case;
                
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
        
        case filter_state is
            when IDLE => 
                if start = '1' then
                    filter_nextstate <= PREP_FILTER;
                elsif set_ba_write = '1' then
                    filter_nextstate <= SEND_WRITE_BA;
                else
                    filter_nextstate <= IDLE;
                end if;
            when SEND_WRITE_BA => 
                if set_ba_read = '1' then
                    filter_nextstate <= IDLE;
                else
                    filter_nextstate <= SEND_WRITE_BA;
                end if;
            when PREP_FILTER => filter_nextstate <= START_CENTER_READ;
            when START_CENTER_READ => filter_nextstate <= WAIT_C_READ;
            when WAIT_C_READ => 
                if sl_sm_done = '1' then
                    filter_nextstate <= START_UPPER_READ;
                else
                    filter_nextstate <= WAIT_C_READ;
                end if;
            when START_UPPER_READ => filter_nextstate <= WAIT_U_READ;
            when WAIT_U_READ => 
                if sl_sm_done = '1' then
                    filter_nextstate <= START_LOWER_READ;
                else
                    filter_nextstate <= WAIT_U_READ;
                end if;
            when START_LOWER_READ => filter_nextstate <= WAIT_L_READ;
            when WAIT_L_READ => 
                if sl_sm_done = '1' then
                    filter_nextstate <= PUSH_PIPELINE;
                else
                    filter_nextstate <= WAIT_L_READ;
                end if;
            when PUSH_PIPELINE => filter_nextstate <= START_WRITE;
            when START_WRITE => filter_nextstate <= WAIT_WRITE;
            when WAIT_WRITE => 
                if sl_sm_done = '1' then
                    filter_nextstate <= INCREMENT_OFFSET;
                else
                    filter_nextstate <= WAIT_WRITE;
                end if;
            when INCREMENT_OFFSET => 
                if current_center_address = end_address then
                    filter_nextstate <= IDLE;
                else
                    filter_nextstate <= START_CENTER_READ;
                end if;
        end case;
        
    end process nextstate_proc;
    
    with filter_state select base_addr_sel <=
        '1' when START_WRITE | WAIT_WRITE | SEND_WRITE_BA,
        '0' when others;
    
    base_address <= read_base_address when base_addr_sel = '0' else corrected_write_base_address;
    current_center_address <= std_logic_vector(unsigned(base_address) + unsigned(addr_offset));
    
    num_cols_padded(15 downto 0) <= num_cols_in;
    num_cols_padded(31 downto 16) <= (others => '0');
    
    with filter_state select curr_col_offset <= 
        num_cols_padded when START_LOWER_READ | WAIT_L_READ,
        std_logic_vector( - signed(num_cols_padded)) when START_UPPER_READ | WAIT_U_READ,
        std_logic_vector(to_unsigned(depth_of_pipeline, 32)) when SEND_WRITE_BA,
        (others => '0') when others;
        
    net_address <= std_logic_vector(unsigned(current_center_address) + unsigned(curr_col_offset));
    addr <= net_address;
    
    end_address <= std_logic_vector(unsigned(numpixels_in) - unsigned(num_cols_padded) - 1);
    

    with filter_state select en1 <= 
        '1' when START_CENTER_READ | WAIT_C_READ | START_UPPER_READ | WAIT_U_READ | START_LOWER_READ | WAIT_L_READ,
        '0' when others;
        
    en2 <= '1' when filter_state = PUSH_PIPELINE else '0';
    
    done <= '1' when filter_state = IDLE else '0';
    
    with filter_state select start_read <= 
        '1' when START_CENTER_READ | START_UPPER_READ | START_LOWER_READ,
        '0' when others;
    
    start_write_out <= '1' when filter_state = START_WRITE else '0';
    write_en <= '1' when filter_state = WAIT_WRITE else '0';
    
    numpixels_out <= numpixels_in when filter_state = IDLE or filter_state = SEND_WRITE_BA else x"00000001";

end Behavioral;
