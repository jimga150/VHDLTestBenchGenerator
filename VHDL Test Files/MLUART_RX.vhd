----------------------------------------------------------------------------------
-- Company:
-- Engineer:
--
-- Create Date:    15:11:20 09/24/2016
-- Design Name:
-- Module Name:    MLUART_RX - Behavioral
-- Project Name:
-- Target Devices:
-- Tool versions:
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
use IEEE.NUMERIC_STD.ALL;
use IEEE.STD_LOGIC_UNSIGNED.ALL;

entity MLUART_RX is
port ( CLK_100MHZ         : in std_logic;
       clk_en_16_x_baud   : in std_logic;
       test_inout1, test_in_out_2 : inout std_logic;
		 read_data_complete : out std_logic;
		 data_out           : out std_logic_vector(7 downto 0);
		 UART_RX            : in std_logic);

end MLUART_RX;

architecture Behavioral of MLUART_RX is

type   tstateRX is (idle, rstart, rstop, rd0, rd1, rd2, rd3, rd4, rd5, rd6, rd7, read_strobe);
signal sstateRX : tstateRX;
signal scount4 : std_logic_vector (3 downto 0) := (others => '0');

signal sdata_out : std_logic_vector (7 downto 0);
signal sdata_read : std_logic_vector (7 downto 0);

begin

data_out <= sdata_out;

-- State Machine: transitions
process(CLK_100MHZ)
begin
  if CLK_100MHZ'event and CLK_100MHZ = '1' then
    if clk_en_16_x_baud = '1' then
	   case sstateRX is
        when idle      => if UART_RX = '0' then sstateRX <= rstart; end if;

		  when rstart    => if scount4 = X"F" then sstateRX <= rd0; end if;
		  when rd0       => if scount4 = X"F" then sstateRX <= rd1; end if;
		  when rd1       => if scount4 = X"F" then sstateRX <= rd2; end if;
		  when rd2       => if scount4 = X"F" then sstateRX <= rd3; end if;
		  when rd3       => if scount4 = X"F" then sstateRX <= rd4; end if;
		  when rd4       => if scount4 = X"F" then sstateRX <= rd5; end if;
		  when rd5       => if scount4 = X"F" then sstateRX <= rd6; end if;
		  when rd6       => if scount4 = X"F" then sstateRX <= rd7; end if;
		  when rd7       => if scount4 = X"F" then sstateRX <= rstop; end if;

		  when rstop     => sstateRX <= read_strobe;
		  when read_strobe => sstateRX <= idle;
		end case;
	 end if;
  end if;
end process;

process(sstateRX)
begin
  case sstateRX is
    when read_strobe =>  read_data_complete <= '1';
	 when others      =>  read_data_complete <= '0';
  end case;
end process;

process(CLK_100MHZ)
begin
  if CLK_100MHZ'event and CLK_100MHZ = '1' then
    if clk_en_16_x_baud = '1' then
      case sstateRX is
		   when rstop => sdata_out <= sdata_read;
		   when others => sdata_out <= sdata_out;
	    end case;
	 end if;
  end if;
end process;

--process(sstateRX, sdata_in)
--begin
--  case sstateRX is
--    --when rstart => sdata_in <= X"00";
--	 when rd0|rd1|rd2|rd3|rd4|rd5|rd6|rd7 => sdata_read <= UART_RX & sdata_in(7 downto 1);
--	 --when rstop  => UART_RX <= '1';
--	 when others => UART_RX <= '1';
--  end case;
--end process;

process(CLK_100MHZ)
begin
  if CLK_100MHZ'event and CLK_100MHZ = '1' then
    if clk_en_16_x_baud = '1' then
       case sstateRX is
		   when rstart|rd0|rd1|rd2|rd3|rd4|rd5|rd6|rd7|rstop => scount4 <= scount4 + '1';
			when others => scount4 <= (others => '0');
		 end case;
	 end if;
  end if;
end process;

process(CLK_100MHZ)
begin
  if CLK_100MHZ'event and CLK_100MHZ = '1' then
    if clk_en_16_x_baud = '1' then
      case sstateRX is
		   --when read_strobe => sdata_out <= sdata_read;
		   when rd0|rd1|rd2|rd3|rd4|rd5|rd6|rd7 => if scount4 = X"8" then sdata_read <=  UART_RX & sdata_read(7 downto 1); end if;
		   when others => null;
	    end case;
	 end if;
  end if;
end process;

end Behavioral;

