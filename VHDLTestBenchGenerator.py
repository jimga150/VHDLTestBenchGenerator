import os
import re
import sys
from enum import Enum, auto, unique
from pathlib import Path


def parse_vhdl(args):
    print(args)

    usage_str = "Usage: java -jar VHDL_testbench_generator.jar <input file> (<output path>)\nFile must be a valid " \
                "VHDL file with no parse errors.\n"

    if len(args) == 0 or len(args[0]) == 0:
        print("Must specify a file.")
        print(usage_str)
        return

    if not (args[0].lower().endswith(".vhd") or args[0].lower().endswith(".vhdl")):
        print("Must specify a VHDL file.")
        print(usage_str)
        return

    input_str = ""
    with open(args[0], "r") as input_file:
        input_str += input_file.read()

    if len(input_str) == 0:
        print("No data found in input file.")
        print(usage_str)
        return

    slash = os.path.sep
    write_path = str(Path.home()) + slash

    if len(args) > 1 and len(args[1]) > 0:
        write_path = args[1]
        if args[1][-1] != slash:
            write_path += slash

    print(input_str)

    module = VHDLModule(input_str)

    if not module.valid:
        print("Invalid VHDL Entity.")
        return

    module.print_info()


class VHDLModule:
    tb_template = "----------------------------------------------------------------------------------\n" \
                  "-- Company: \n" \
                  "-- Engineer: \n" \
                  "-- \n" \
                  "-- Create Date: {{CURR_DATE}}\n" \
                  "-- Design Name: {{TESTBENCH_NAME}}\n" \
                  "-- Module Name: {{TESTBENCH_NAME}} - Behavioral\n" \
                  "-- Project Name: \n" \
                  "-- Target Devices: \n" \
                  "-- Tool Versions: \n" \
                  "-- Description: \n" \
                  "-- \n" \
                  "-- Dependencies: \n" \
                  "-- \n" \
                  "-- Revision:\n" \
                  "-- Revision 0.01 - File Created\n" \
                  "-- Additional Comments: Created with VHDL Test Bench Template Generator\n" \
                  "-- \n" \
                  "----------------------------------------------------------------------------------\n" \
                  "\n" \
                  "\n" \
                  "library IEEE;\n" \
                  "use IEEE.STD_LOGIC_1164.ALL;\n" \
                  "\n" \
                  "-- Uncomment the following library declaration if using\n" \
                  "-- arithmetic functions with Signed or Unsigned values\n" \
                  "{{NUMERIC_COMMENT}}use IEEE.NUMERIC_STD.ALL;\n" \
                  "\n" \
                  "-- Uncomment the following library declaration if instantiating\n" \
                  "-- any Xilinx leaf cells in this code.\n" \
                  "--library UNISIM;\n" \
                  "--use UNISIM.VComponents.all;\n" \
                  "\n" \
                  "entity {{TESTBENCH_NAME}} is\n" \
                  "end {{TESTBENCH_NAME}};\n" \
                  "\n" \
                  "architecture Behavioral of {{TESTBENCH_NAME}} is\n" \
                  "    \n" \
                  "    {{GENERIC_PARAM_DECL}}\n" \
                  "    {{INPUT_SIGNAL_DECL}}\n" \
                  "    {{INOUT_SIGNAL_DECL}}\n" \
                  "    {{OUTPUT_SIGNAL_DECL}}\n" \
                  "    {{CLOCK_PERIOD_DECL}}\n" \
                  "begin\n" \
                  "    \n" \
                  "    UUT: entity work.{{MODULE_NAME}}\n" \
                  "    {{GENERIC_MAP}}{{PORT_MAP}}\n" \
                  "    \n" \
                  "    {{CLOCK_DRIVERS}}\n" \
                  "    stim_proc: process is begin\n" \
                  "        \n" \
                  "        {{STD_WAIT}}\n" \
                  "        {{RESETS_INACTIVE}}\n" \
                  "        {{STD_WAIT}}\n" \
                  "        --Insert stimuli here\n" \
                  "        \n" \
                  "        assert false report \"End Simulation\" severity failure;\n" \
                  "        \n" \
                  "    end process;\n" \
                  "\n" \
                  "end Behavioral;\n"

    ports = []
    generics = []
    clocks = []
    resets = []

    name = ""

    valid = False

    def __init__(self, input_str):

        input_str = self.removeVHDLComments(input_str)

        things_to_space_out = [
            ["[(]", "("],
            ["[)]", ")"],
            ["[;]", ";"],
            ["[,]", ","],

            # parlor trick incoming
            ["[:][=]", "!="],
            ["[=][>]", "=!"],
            ["[:]", ":"],
            ["[!][=]", ":="],
            ["[=][!]", "=>"]
        ]

        for pair in things_to_space_out:
            # input_str = input_str.replace(pair[0], " " + pair[1] + " ")
            input_str = re.sub(pair[0], " " + pair[1] + " ", input_str)

        words = re.split("\\s+", input_str)

        entity_found = False
        generic_found = False
        port_found = False

        generic_names = []
        generic_type = ""
        generic_default_val = ""

        port_names = []
        port_direction = ""
        port_type = ""
        interface_range = ""

        i = 0
        while i < len(words):

            # print(words[i])

            if (not entity_found) and words[i].lower() == "entity":
                self.name = words[i + 1]
                print("Entity: " + self.name)
                entity_found = True
                i += 1
                continue

            if entity_found and (not generic_found) and words[i].lower() == "generic":
                generic_found = True
                i += 2
                continue

            if entity_found and (not port_found) and words[i].lower() == "port":
                generic_found = True  # no generics but we move past it
                port_found = True
                i += 2
                continue

            # print(entity_found, generic_found, port_found)

            if entity_found and generic_found and (not port_found):

                if words[i] == ",":
                    i += 1
                    continue

                if words[i] == ":":
                    generic_type = words[i + 1]
                    if words[i + 2] == "(":
                        interface_range = words[i + 3] + " " + words[i + 4] + " " + words[i + 5]

                        if words[i + 8] == "(" and words[i + 9].lower() == "others":
                            generic_default_val = "(others => " + words[i + 11] + ")"
                            i += 14
                        else:
                            generic_default_val = words[i + 8]
                            i += 10

                    else:
                        interface_range = ""
                        generic_default_val = words[i + 3]
                        i += 5

                    for generic_name in generic_names:
                        self.generics.append(Generic(generic_name, generic_type, generic_default_val, interface_range))

                    generic_names = []
                    continue

                generic_names.append(words[i])

            if entity_found and generic_found and port_found:

                if words[i] == ",":
                    i += 1
                    continue

                if words[i] == ":":
                    port_direction = words[i + 1]
                    port_type = words[i + 2]

                    if words[i + 3] == "(":

                        w = 4
                        range_str = ""
                        while not words[i + w] == ")":
                            range_str += words[i + w] + " "
                            w += 1

                        interface_range = range_str[:-1]  # remove last space
                        i = i + w + 2

                    else:
                        interface_range = ""
                        i = i + 4

                    for port_name in port_names:
                        self.ports.append(Port(port_name, port_direction, port_type, interface_range))

                    port_names = []
                    continue

                if words[i].lower() == "end":
                    break

                port_names.append(words[i])

            i = i + 1

        if not entity_found:
            print("No entity found.")
            return

        if not port_found:
            print("No ports found.")
            return

        # find clocks
        # Strategy 1: look for "rising_edge" and "falling_edge"
        for i in range(0, len(words)):
            pol = PolarityType.INVALID

            if words[i].lower() == "rising_edge":
                pol = PolarityType.POSITIVE
            elif words[i].lower() == "falling_edge":
                pol = PolarityType.NEGATIVE
            else:
                continue

            name = words[i + 2]
            if self.clk_port_invalid(name): continue

            clock_port = False
            for p in self.ports:
                if p.name == name:
                    clock_port = p
                    self.ports.remove(p)
                    break

            self.clocks.append(Clock(clock_port, pol))

        # Strategy 2: look for manual instances of the strategy 1 function names
        for i in range(0, len(words)):
            if "'event" in words[i].lower():
                name = re.split("[']", words[i])[0]

                if self.clk_port_invalid(name): continue

                # Will only handle finding these two cases:
                # <clk>'event and <clk> = '<val>'
                # <clk> = '<val>' and <clk>'event
                edge_val = ""
                if words[i + 1].lower() == "and" and words[i + 2].lower() == name.lower():
                    edge_val = words[i + 4]
                elif words[i - 1].lower() == "and" and words[i - 4].lower() == name.lower():
                    edge_val = words[i - 2]
                else:
                    continue

                clock_port = False  # TODO: default clock constructor
                for p in self.ports:
                    if p.name == name:
                        clock_port = p
                        self.ports.remove(p)
                        break

                if edge_val == "'1'":
                    self.clocks.append(Clock(clock_port, PolarityType.POSITIVE))
                elif edge_val == "'0'":
                    self.clocks.append(Clock(clock_port, PolarityType.NEGATIVE))

        # Find reset ports
        # Literally just find any port containing "rst" or "reset" and if it ends in 'n', its negative
        toRemove = []
        for p in self.ports:
            if "rst" in p.name.lower() or "reset" in p.name.lower():
                if p.dir != PortDir.IN: continue
                if p.is_bus(): continue

                pol = PolarityType.INVALID
                if p.name.lower()[-1] == 'n':
                    pol = PolarityType.NEGATIVE
                else:
                    pol = PolarityType.POSITIVE

                toRemove.append(p)
                self.resets.append(Reset(p, pol))

        for p in toRemove:
            self.ports.remove(p)

        self.valid = True

    def print_info(self):
        print("\nGenerics:")

        if len(self.generics) == 0:
            print("None found.")
        else:
            for g in self.generics:
                print(g.toString())

        print("\nClock Ports:")
        if len(self.clocks) == 0:
            print("None found.")
        else:
            for c in self.clocks:
                print(c.port.port_decl_string() + " : " + c.polarity_toString())

        print("\nReset Ports:")
        if len(self.resets) == 0:
            print("None found.")
        else:
            for r in self.resets:
                print(r.port.port_decl_string() + " : " + r.polarity_toString())

        print("\nOther Ports:")
        if len(self.ports) == 0:
            print("None found.")
        else:
            for p in self.ports:
                print(p.port_decl_string())

    def removeVHDLComments(self, commented):

        lines = re.split("[\r\n]", commented)

        for l in range(0, len(lines)):

            if len(lines[l]) == 0:
                continue

            i = lines[l].find("--")
            if i == 0:
                lines[i] = ""
            elif i > 0:
                lines[l] = lines[l][:i]

        ans = ""
        for l in range(0, len(lines)):
            ans += lines[l] + "\n"

        return ans

    def clk_port_invalid(self, name):

        name_match = False
        port_index = -1

        for i in range(0, len(self.ports)):
            p = self.ports[i]
            if p.name.lower() == name.lower():
                name_match = True
                port_index = i
                break

        if not name_match: return True

        port = self.ports[port_index]

        if port.is_bus(): return True

        return port.dir != PortDir.IN


@unique
class PortDir(Enum):
    INVALID = auto()
    IN = auto()
    OUT = auto()
    INOUT = auto()


@unique
class PolarityType(Enum):
    POSITIVE = auto()
    NEGATIVE = auto()
    INVALID = auto()


class VHDLInterface:
    name = ""
    interface_type = ""
    interface_range = ""

    def __init__(self, name, interface_type, interface_range):
        self.name = name
        self.interface_type = interface_type
        self.interface_range = interface_range

    @classmethod
    def default(cls):
        return cls("<INTERFACE_NAME>", "<INTERFACE_TYPE>", "<INTERFACE_RANGE>")

    def is_bus(self):
        return len(self.interface_range) > 0


# TODO: add default values to ports (really promote the item to VHDLInterface)
class Port(VHDLInterface):
    dir = PortDir.INVALID

    def __init__(self, name, dir_str, port_type, port_range):
        super().__init__(name, port_type, port_range)
        self.dir = self.decode_port_dir(dir_str)

    @classmethod
    def default(cls):
        return cls("<PORT_NAME>", "<PORT_DIR>", "<PORT_TYPE>", "<PORT_RANGE>")

    def toString(self):
        range_str = "(" + str(self.interface_range) + ")" if self.is_bus() else ""
        return self.name + " : " + self.interface_type + range_str

    def port_decl_string(self):
        return self.toString().replace(" : ", " : " + self.port_dir_toString() + " ")

    def decode_port_dir(self, port_dir_str):
        port_dir_str = port_dir_str.lower()
        if port_dir_str == "in": return PortDir.IN
        if port_dir_str == "out": return PortDir.OUT
        if port_dir_str == "inout": return PortDir.INOUT
        return PortDir.INVALID

    def port_dir_toString(self):
        if self.dir == PortDir.IN: return "in"
        if self.dir == PortDir.OUT: return "out"
        if self.dir == PortDir.INOUT: return "inout"
        return "<ERROR>"


class Generic(VHDLInterface):
    default_val = ""

    def __init__(self, name, generic_type, default_val, generic_range):
        super().__init__(name, generic_type, generic_range)
        self.default_val = default_val

    def toString(self):
        range_str = "(" + str(self.interface_range) + ")" if self.is_bus() else ""
        return self.name + " : " + self.interface_type + range_str + " := " + self.default_val


class VHDLControlInput:
    port = Port.default()

    polarity = PolarityType.INVALID

    def __init__(self, port, pol):
        self.port = port
        self.polarity = pol

    def reverse_polarity(self, orig):
        if orig == PolarityType.INVALID: return orig
        return PolarityType.NEGATIVE if orig == PolarityType.POSITIVE else PolarityType.POSITIVE


class Clock(VHDLControlInput):

    def __init__(self, port, pol):
        super().__init__(port, pol)
        assert port.dir == PortDir.IN

    def polarity_toString(self):
        if self.polarity == PolarityType.POSITIVE:
            return "Rising Edge"
        if self.polarity == PolarityType.NEGATIVE:
            return "Falling Edge"

        return "Invalid Polarity"

    def period_name(self):
        return self.port.name + "_period"


class Reset(VHDLControlInput):

    def __init__(self, port, pol):
        super().__init__(port, pol)
        assert port.dir == PortDir.IN

    def polarity_toString(self):
        if self.polarity == PolarityType.POSITIVE:
            return "Active High"
        if self.polarity == PolarityType.NEGATIVE:
            return "Active Low"

        return "Invalid Polarity"


if __name__ == '__main__':
    parse_vhdl(sys.argv[1:])
