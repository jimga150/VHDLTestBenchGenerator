import os
import re
import sys
from enum import Enum, auto, unique
from pathlib import Path
from datetime import datetime
import argparse


def parse_vhdl(args):
    parser = argparse.ArgumentParser(
        description="Generates a testbench template for a VHDL module, including clock and reset detection. File must "
                    "be a valid VHDL file with no parse errors. It must contain only one entity with at least one "
                    "input port, and the generated testbench will use the first architecture in the file to gather "
                    "relevant information. "
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="verbose mode")
    parser.add_argument("-s", "--spaces", help="use a number of spaces instead of tab characters")
    parser.add_argument("--clkport", help="specify a string that indicates a clock port")
    parser.add_argument("--rstport", help="specify a string that indicates a reset port")
    parser.add_argument("input_file", help="The VHDL module file to generate the testbench template for")

    group = parser.add_mutually_exclusive_group()
    group.add_argument("--outpath", help="path to write template to (as <modulename>_tb.vhd")
    group.add_argument("-o", "--out", help="output file. if neither --outpath nor --out is specified, testbench "
                                           "template is written to the home directory.")

    parsed_args = parser.parse_args(args)
    input_file = parsed_args.input_file
    outpath = parsed_args.outpath
    outfile = parsed_args.out
    verbose_mode = parsed_args.verbose
    spaces_enabled = parsed_args.spaces
    clk_substr = parsed_args.clkport
    rst_substr = parsed_args.rstport

    if verbose_mode:
        print("args:")
        print(args)
        print(parsed_args)

    if not (input_file.lower().endswith(".vhd") or input_file.lower().endswith(".vhdl")):
        print("Must specify a VHDL file.")
        parser.print_help()
        return

    input_str = ""
    try:
        with open(input_file, "r") as infile:
            input_str += infile.read()
    except OSError as e:
        print("Input file read error:\n" + str(e))
        parser.print_help()
        return

    if len(input_str) == 0:
        print("No data found in input file.")
        parser.print_help()
        return

    if verbose_mode:
        print(input_str)

    module = VHDLModule()

    module.clk_substr = clk_substr
    module.rst_substr = rst_substr

    module.use(input_str)

    if not module.valid:
        print("Invalid VHDL Entity.")
        parser.print_help()
        return

    if verbose_mode:
        module.print_info()

    test_bench_str = module.build_test_bench_str()

    if spaces_enabled:
        # replace all tabs with 4 spaces each
        test_bench_str = re.sub("[\t]", "    ", test_bench_str)

    if verbose_mode:
        print(test_bench_str)

    slash = os.path.sep
    write_path = str(Path.home()) + slash

    if not (outfile is None):
        write_path = outfile
    elif not (outpath is None):
        write_path = outpath
        if write_path[-1] != slash:
            write_path += slash

    out_file_name = write_path

    if outfile is None:
        # find original file name, without the extension
        # generate test bench file name
        # print(input_file)
        split_path = re.split("[.\\/]", input_file)
        # print(split_path)
        filename = split_path[-2]
        out_file_name += filename + "_tb.vhd"

    try:

        with open(out_file_name, "w") as out_file:
            out_file.write(test_bench_str)

        print("Written testbench to " + out_file_name + ". Happy HDLing.")

    except OSError:
        print("\nTestbench write failed( " + out_file_name
              + " ) testbench template output will be printed for you to copy:\n\n\n")
        print(test_bench_str)


class VHDLModule:
    comment_delim_str = "--"

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
                  "{{LIBRARIES}}\n" \
                  "entity {{TESTBENCH_NAME}} is\n" \
                  "end {{TESTBENCH_NAME}};\n" \
                  "\n" \
                  "architecture Behavioral of {{TESTBENCH_NAME}} is\n" \
                  "\t\n" \
                  "\t{{GENERIC_PARAM_DECL}}\n" \
                  "\t{{INPUT_SIGNAL_DECL}}\n" \
                  "\t{{IN_OUT_SIGNAL_DECL}}\n" \
                  "\t{{OUTPUT_SIGNAL_DECL}}\n" \
                  "\t{{CLOCK_PERIOD_DECL}}\n" \
                  "begin\n" \
                  "\t\n" \
                  "\tUUT: entity work.{{MODULE_NAME}}\n" \
                  "\t{{GENERIC_MAP}}{{PORT_MAP}}\n" \
                  "\t\n" \
                  "\t{{CLOCK_DRIVERS}}\n" \
                  "\tstim_proc: process is begin\n" \
                  "\t\t\n" \
                  "\t\t{{STD_WAIT}}\n" \
                  "\t\t{{RESETS_INACTIVE}}\n" \
                  "\t\t{{STD_WAIT}}\n" \
                  "\t\t--Insert stimuli here\n" \
                  "\t\t\n" \
                  "\t\tassert false report \"End Simulation\" severity failure;\n" \
                  "\t\t\n" \
                  "\t\t-- Not strictly necessary, but prevents process from looping \n" \
                  "\t\t-- if the above assert statement is removed\n" \
                  "\t\twait;\n" \
                  "\t\t\n" \
                  "\tend process;\n" \
                  "\n" \
                  "end Behavioral;\n"

    library_includes = ""

    ports = []
    generics = []
    clocks = []
    resets = []

    clk_substr = None
    rst_substr = None

    name = ""

    valid = False

    def __init__(self):
        pass

    def use(self, input_str):
        input_str = VHDLModule.remove_vhdl_comments(input_str)

        things_to_space_out = [
            ["[(]", "("],
            ["[)]", ")"],
            ["[;]", ";"],
            ["[,]", ","],

            # Parlor trick incoming: What is happening here is I cant go and run a replace looking for colons because
            # it will catch all the colon-equals assignments, and it's not easy, and more importantly not portable,
            # to try to distinguish between colon-equals and any other valid use of a colon in VHDL. Instead,
            # I replace all colon-equals assignments with exclamation-mark equals, which is something not used at all
            # in VHDL (not-equals is "/=" in this language). Then, i can space out colons, and the switch the
            # exclamation-mark-equals pairs with spaced out colon-equals again. The side effect is that these will be
            # double spaced out, but this doesnt matter since the split algorithm will delete any empty items after
            # splitting.
            ["[:][=]", "!="],
            ["[=][>]", "=!"],
            ["[:]", ":"],
            ["[!][=]", ":="],
            ["[=][!]", "=>"]
        ]

        # space out assignments for parsing consistency
        for pair in things_to_space_out:
            # input_str = input_str.replace(pair[0], " " + pair[1] + " ")
            input_str = re.sub(pair[0], " " + pair[1] + " ", input_str)

        # split input file into an array of items which will be individually traversed to parse the whole file.
        words = re.split("\\s+", input_str)

        entity_found = False
        generic_found = False
        port_found = False

        generic_names = []
        port_names = []

        library_definitions = []

        i = 0
        while i < len(words):

            if words[i].lower() == "library" or words[i].lower() == "use":

                offset_index = 0
                while words[i + offset_index] != ";":
                    library_definitions.append(words[i + offset_index])
                    offset_index += 1

                library_definitions.append(words[i + offset_index] + "\n")

            # detecting the 'entity' statement
            if (not entity_found) and words[i].lower() == "entity":
                self.name = words[i + 1]
                # print("Entity: " + self.name)
                entity_found = True
                i += 1
                continue

            # detecting the 'generic' statement, but only after we detected 'entity'
            if entity_found and (not generic_found) and words[i].lower() == "generic":
                generic_found = True
                i += 2
                continue

            # detecting the 'port' statement, but only after we detected 'entity' (if we havent detected a generic
            # statement yet, just let it slide since that's optional)
            if entity_found and (not port_found) and words[i].lower() == "port":
                generic_found = True  # no generics but we move past it
                port_found = True
                i += 2
                continue

            # print(entity_found, generic_found, port_found)

            # Generic item detection. look for commas and colons to delimit names, types, ranges, and default values
            if entity_found and generic_found and (not port_found):

                if words[i] == ",":
                    i += 1
                    continue

                # found a colon, meaning that the non-comma words before this were generic names.
                if words[i] == ":":
                    generic_type = words[i + 1]
                    if words[i + 2] == "(":  # item is a bus
                        interface_range = words[i + 3] + " " + words[i + 4] + " " + words[i + 5]

                        if words[i + 8] == "(" and words[i + 9].lower() == "others":
                            generic_default_val = "(others => " + words[i + 11] + ")"
                            i += 14
                        else:
                            generic_default_val = words[i + 8]
                            i += 10

                    else:  # item is NOT a bus
                        interface_range = ""
                        generic_default_val = words[i + 3]
                        i += 5

                    for generic_name in generic_names:
                        self.generics.append(Generic(generic_name, generic_type, interface_range, generic_default_val))

                    generic_names = []
                    continue

                # keep recording the names of the generics otherwise
                generic_names.append(words[i])

            # port detection mode: much like generic detection, but these items have directions,
            # and default values are optional.
            if entity_found and generic_found and port_found:

                if words[i] == ",":
                    i += 1
                    continue

                if words[i] == ":":
                    port_direction = words[i + 1]
                    port_type = words[i + 2]

                    if words[i + 3] == "(":  # Range detected

                        range_offset = 4
                        range_str = ""
                        while not words[i + range_offset] == ")":
                            range_str += words[i + range_offset] + " "
                            range_offset += 1

                        interface_range = range_str[:-1]  # remove last space

                    else:
                        interface_range = ""
                        range_offset = 2

                    if words[i + range_offset + 1] == ":=":  # Default val detected

                        d_offset = 2
                        default_val = ""
                        while words[i + range_offset + d_offset] != ";":
                            default_val += words[i + range_offset + d_offset] + " "
                            d_offset += 1

                        # Special treatment: un-space out parentheses
                        default_val = re.sub("[ ][(][ ]", "(", default_val)
                        default_val = re.sub("[ ][)][ ]", ")", default_val)

                        if default_val[-1] == " ":
                            default_val = default_val[:-1]  # remove last space

                    else:
                        default_val = None
                        d_offset = 1

                    i = i + range_offset + d_offset + 1  # skip semiolon

                    for port_name in port_names:
                        self.ports.append(Port(port_name, port_direction, port_type, interface_range, default_val))

                    port_names = []
                    continue

                if words[i].lower() == "end":
                    break

                port_names.append(words[i])

            i = i + 1

        for item in library_definitions:
            if item[0] == ';' and self.library_includes[-1] == ' ':  # remove last space
                self.library_includes = self.library_includes[:-1]

            self.library_includes += item

            if item[-1] != '\n':  # Add space if this isn't the carriage return
                self.library_includes += " "

        if not entity_found:
            print("No entity found.")
            return

        if not port_found:
            # assume that ports are essential to a design: if you're not using any, why is this its own entity
            # anyways? and especially, why make a test bench for it?
            print("No ports found.")
            return

        # find clocks
        # Strategy 1: look for "rising_edge" and "falling_edge" convenience functions
        for i in range(0, len(words)):

            if words[i].lower() == "rising_edge":
                pol = PolarityType.POSITIVE
            elif words[i].lower() == "falling_edge":
                pol = PolarityType.NEGATIVE
            else:
                continue

            name = words[i + 2]  # TODO: encapsulate clock port adding
            if self.clk_port_invalid(name):
                continue

            clock_port = False
            for p in self.ports:
                if p.name == name:
                    clock_port = p
                    self.ports.remove(p)
                    break

            self.clocks.append(Clock(clock_port, pol))

        # Strategy 2: look for manual instances of clock usages: the "'edge" property
        for i in range(0, len(words)):
            if "'event" in words[i].lower():
                name = re.split("[']", words[i])[0]

                if self.clk_port_invalid(name):
                    continue

                # Will only handle finding these two cases:
                # <clk>'event and <clk> = '<val>'
                # <clk> = '<val>' and <clk>'event
                if words[i + 1].lower() == "and" and words[i + 2].lower() == name.lower():
                    edge_val = words[i + 4]
                elif words[i - 1].lower() == "and" and words[i - 4].lower() == name.lower():
                    edge_val = words[i - 2]
                else:
                    continue

                clock_port = Clock.default()
                for p in self.ports:
                    if p.name == name:
                        clock_port = p
                        self.ports.remove(p)
                        break

                if edge_val == "'1'":
                    self.clocks.append(Clock(clock_port, PolarityType.POSITIVE))
                elif edge_val == "'0'":
                    self.clocks.append(Clock(clock_port, PolarityType.NEGATIVE))

        # Strategy 3 for clock finding: any port containing 'clk', 'clock', 'clck'
        to_remove = []
        for p in self.ports:
            lcase_pname = p.name.lower()
            if "clk" in lcase_pname or "clock" in lcase_pname or "clck" in lcase_pname or \
                    (self.clk_substr is not None and self.clk_substr in lcase_pname):

                if p.dir != PortDir.IN:
                    continue

                if p.is_bus():
                    continue

                if p.name.lower()[-1] == 'n':
                    pol = PolarityType.NEGATIVE
                else:
                    pol = PolarityType.POSITIVE

                to_remove.append(p)
                self.clocks.append(Clock(p, pol))

        # Find reset ports
        # Literally just find any port containing "rst" or "reset" and if it ends in 'n', its negative
        for p in self.ports:
            lcase_pname = p.name.lower()
            if "rst" in lcase_pname or "reset" in lcase_pname or \
                    (self.rst_substr is not None and self.rst_substr in lcase_pname):

                if p.dir != PortDir.IN:
                    continue

                if p.is_bus():
                    continue

                if p.name.lower()[-1] == 'n':
                    pol = PolarityType.NEGATIVE
                else:
                    pol = PolarityType.POSITIVE

                to_remove.append(p)
                self.resets.append(Reset(p, pol))

        for p in to_remove:
            self.ports.remove(p)

        self.valid = True

    def build_test_bench_str(self):
        # most of this is plain, honest, replacement of template keywords.

        test_bench_str = self.tb_template

        test_bench_str = re.sub("{{LIBRARIES}}", self.library_includes, test_bench_str)
        test_bench_str = re.sub("{{MODULE_NAME}}", self.name, test_bench_str)
        test_bench_str = re.sub("{{TESTBENCH_NAME}}", self.name + "_tb", test_bench_str)

        now = datetime.now()
        datetime_str = now.strftime("%m/%d/%Y %H:%M:%S")
        test_bench_str = re.sub("{{CURR_DATE}}", datetime_str, test_bench_str)

        generic_declarations = ""
        for g in self.generics:
            generic_declarations += "constant " + str(g) + ";\n\t"

        # You'll see this line and its siblings scattered throughout this function, just to keep the line skips
        # consistent.
        if len(self.generics) > 0:
            generic_declarations += "\n\t"

        port_input_decl = ""
        port_in_out_decl = ""
        port_output_decl = ""

        if len(self.clocks) > 0:
            port_input_decl += self.comment_delim_str + "Clocks\n\t"

        for c in self.clocks:
            default_val = VHDLModule.get_default_val_for(c.port.interface_type, c.polarity)

            port_input_decl += "signal " + str(c.port) + " := " + default_val + ";\n\t"

        if len(self.clocks) > 0:
            port_input_decl += "\n\t"

        # add resets
        if len(self.resets) > 0:
            port_input_decl += self.comment_delim_str + "Resets\n\t"

        for r in self.resets:
            default_val = \
                VHDLModule.get_default_val_for(r.port.interface_type, PolarityType.reverse_polarity(r.polarity))
            port_input_decl += "signal " + str(r.port) + " := " + default_val + ";\n\t"

        if len(self.resets) > 0:
            port_input_decl += "\n\t"

        found_input = False

        for p in self.ports:
            if p.dir == PortDir.IN:

                if not found_input:
                    found_input = True
                    port_input_decl += self.comment_delim_str + "General inputs\n\t"

                if p.default_val is None:
                    p.default_val = VHDLModule.get_default_val_for(p.interface_type, PolarityType.POSITIVE)

                port_input_decl += "signal " + str(p) + " := " + p.default_val + ";\n\t"

            elif p.dir == PortDir.INOUT:

                if p.default_val is None:
                    p.default_val = VHDLModule.get_default_val_for(p.interface_type, PolarityType.POSITIVE)

                port_in_out_decl += "signal " + str(p) + " := " + p.default_val + ";\n\t"

            elif p.dir == PortDir.OUT:

                port_output_decl += "signal " + str(p) + ";\n\t"

            else:
                print("ERROR: Port direction undefined: " + p.dir)
                return ""

        clock_periods = ""
        for c in self.clocks:
            clock_periods += "constant " + c.period_name() + " : time := 10 ns;\n\t"

        if len(generic_declarations) > 0:
            generic_declarations = self.comment_delim_str + "Generics\n\t" + generic_declarations
            generic_declarations += "\n\t"

        if len(port_input_decl) > 0:
            port_input_decl += "\n\t"

        if len(port_in_out_decl) > 0:
            port_in_out_decl = self.comment_delim_str + "In-Outs\n\t" + generic_declarations
            port_in_out_decl += "\n\t"

        if len(port_output_decl) > 0:
            port_output_decl = self.comment_delim_str + "Outputs\n\t" + port_output_decl
            port_output_decl += "\n\t"

        if len(clock_periods) > 0:
            clock_periods = "\n\t" + self.comment_delim_str + "Clock Periods\n\t" + clock_periods

        test_bench_str = re.sub("{{GENERIC_PARAM_DECL}}[\\n]([ ]{4}|\\t)", generic_declarations, test_bench_str)
        test_bench_str = re.sub("{{INPUT_SIGNAL_DECL}}[\\n]([ ]{4}|\\t)", port_input_decl, test_bench_str)
        test_bench_str = re.sub("{{IN_OUT_SIGNAL_DECL}}[\\n]([ ]{4}|\\t)", port_in_out_decl, test_bench_str)
        test_bench_str = re.sub("{{OUTPUT_SIGNAL_DECL}}[\\n]([ ]{4}|\\t)", port_output_decl, test_bench_str)

        test_bench_str = re.sub("[\\n]([ ]{4}|\\t){{CLOCK_PERIOD_DECL}}", clock_periods, test_bench_str)

        # build generic map
        if len(self.generics) > 0:
            generic_map = "generic map("
            for i in range(0, len(self.generics)):
                g = self.generics[i]
                generic_map += "\n\t\t" + g.name + " => " + g.name
                if i < len(self.generics) - 1:
                    generic_map += ","

            generic_map += "\n\t)\n\t"
            test_bench_str = re.sub("{{GENERIC_MAP}}", generic_map, test_bench_str)
        else:
            test_bench_str = re.sub("{{GENERIC_MAP}}", "", test_bench_str)

        # Build port map
        port_map = "port map("
        for i in range(0, len(self.clocks)):
            p = self.clocks[i].port
            port_map += "\n\t\t" + p.name + " => " + p.name
            if len(self.resets) > 0 or len(self.ports) > 0 or i < len(self.clocks) - 1:
                port_map += ","

        for i in range(0, len(self.resets)):
            p = self.resets[i].port
            port_map += "\n\t\t" + p.name + " => " + p.name
            if len(self.ports) > 0 or i < len(self.resets) - 1:
                port_map += ","

        for i in range(0, len(self.ports)):
            p = self.ports[i]
            port_map += "\n\t\t" + p.name + " => " + p.name
            if i < len(self.ports) - 1:
                port_map += ","

        port_map += "\n\t);"
        test_bench_str = re.sub("{{PORT_MAP}}", port_map, test_bench_str)

        # clock driving statements
        clock_drivers = ""
        for c in self.clocks:
            clock_drivers += c.port.name + " <= not " + c.port.name + " after " + c.period_name() + "/2;\n\t"

        if len(clock_drivers) > 0:
            clock_drivers = self.comment_delim_str + "Clock Drivers\n\t" + clock_drivers

        test_bench_str = re.sub("{{CLOCK_DRIVERS}}", clock_drivers, test_bench_str)

        deassert_resets = ""
        for r in self.resets:
            deassert_resets += \
                r.port.name + \
                " <= " + \
                VHDLModule.get_default_val_for(r.port.interface_type, r.polarity) + \
                ";\n\t\t"

        deassert_resets += "\n\t\t"
        test_bench_str = re.sub("{{RESETS_INACTIVE}}[\n][\t]{2}", deassert_resets, test_bench_str)

        if len(self.resets) == 0:
            # replace only the first occurrence
            test_bench_str = re.sub("[\n][\t]{2}{{STD_WAIT}}[\n][\t]{2}", "", test_bench_str, 1)

        # First clock is used for master clock period waits by default
        if len(self.clocks) > 0:
            clock_per_wait = "wait for " + self.clocks[0].period_name() + ";\n\t\t"
            test_bench_str = re.sub("{{STD_WAIT}}", clock_per_wait, test_bench_str)
        else:
            test_bench_str = re.sub("{{STD_WAIT}}\n[\t]{2}", "", test_bench_str)

        return test_bench_str

    def print_info(self):
        print("\nLibraries:")
        print(self.library_includes)

        print("\nGenerics:")

        if len(self.generics) == 0:
            print("None found.")
        else:
            for g in self.generics:
                print(str(g))

        print("\nClock Ports:")
        if len(self.clocks) == 0:
            print("None found.")
        else:
            for c in self.clocks:
                print(str(c))

        print("\nReset Ports:")
        if len(self.resets) == 0:
            print("None found.")
        else:
            for r in self.resets:
                print(str(r))

        print("\nOther Ports:")
        if len(self.ports) == 0:
            print("None found.")
        else:
            for p in self.ports:
                print(p.port_decl_string())

        print("\n\n")

    @staticmethod
    def remove_vhdl_comments(commented):
        # bust em open boys
        lines = re.split("[\r\n]", commented)

        for line_index in range(0, len(lines)):

            if len(lines[line_index]) == 0:
                continue

            # if we find a comment, take it out, or delete the line if its all comment.
            i = lines[line_index].find(VHDLModule.comment_delim_str)
            if i == 0:
                lines[line_index] = ""
            elif i > 0:
                lines[line_index] = lines[line_index][:i]

        # reassemble the test file
        ans = ""
        for line_index in range(0, len(lines)):
            ans += lines[line_index] + "\n"

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

        if not name_match:
            return True

        port = self.ports[port_index]

        if port.is_bus():
            return True

        return port.dir != PortDir.IN

    @staticmethod
    def get_default_val_for(type_in, polarity):
        default_vals = [

            ["std_logic", "'0'", "'1'"],
            ["std_logic_vector", "(others => '0')", "(others => '1')"],

            ["std_ulogic", "'0'", "'1'"],
            ["std_ulogic_vector", "(others => '0')", "(others => '1')"],

            ["bit", "'0'", "'1'"],
            ["bit_vector", "(others => '0')", "(others => '1')"],

            ["unsigned", "(others => '0')", "(others => '1')"],
            ["signed", "(others => '0')", "(others => '1')"],

            ["integer", "0", "1"],
            ["natural", "0", "1"]
        ]

        for pair in default_vals:
            if pair[0].lower() == type_in.lower():
                return pair[2] if polarity == PolarityType.NEGATIVE else pair[1]

        return "<DEFAULT VALUE NOT FOUND>"


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

    @staticmethod
    def reverse_polarity(pol):
        if pol == PolarityType.INVALID:
            return pol

        return PolarityType.POSITIVE if pol == PolarityType.NEGATIVE else PolarityType.NEGATIVE


class VHDLInterface:
    name = ""
    interface_type = ""
    interface_range = ""
    default_val = ""

    def __init__(self, name, interface_type, interface_range, default_val):
        self.name = name
        self.interface_type = interface_type
        self.interface_range = interface_range
        self.default_val = default_val

    @classmethod
    def default(cls):
        return cls("<INTERFACE_NAME>", "<INTERFACE_TYPE>", "<INTERFACE_RANGE>", "<DEFAULT_VAL>")

    def is_bus(self):
        return len(self.interface_range) > 0 and self.interface_range != "<INTERFACE_RANGE>"


class Port(VHDLInterface):
    dir = PortDir.INVALID

    def __init__(self, name, dir_str, port_type, port_range, default_val=None):
        super().__init__(name, port_type, port_range, default_val)
        self.dir = Port.decode_port_dir(dir_str)

    @classmethod
    def default(cls):
        return cls("<PORT_NAME>", "<PORT_DIR>", "<PORT_TYPE>", "<PORT_RANGE>", "<PORT_DEFAULT_VAL>")

    def __str__(self):
        range_str = "(" + str(self.interface_range) + ")" if self.is_bus() else ""
        return self.name + " : " + self.interface_type + range_str

    def port_decl_string(self):

        if not (self.default_val is None):
            default_assignment = " := " + self.default_val
        else:
            default_assignment = ""

        return str(self).replace(" : ", " : " + self.port_dir_string() + " ") + default_assignment

    @staticmethod
    def decode_port_dir(port_dir_str):

        port_dir_str = port_dir_str.lower()

        if port_dir_str == "in":
            return PortDir.IN

        if port_dir_str == "out":
            return PortDir.OUT

        if port_dir_str == "inout":
            return PortDir.INOUT

        return PortDir.INVALID

    def port_dir_string(self):

        if self.dir == PortDir.IN:
            return "in"

        if self.dir == PortDir.OUT:
            return "out"

        if self.dir == PortDir.INOUT:
            return "inout"

        return "<ERROR>"


class Generic(VHDLInterface):

    def __str__(self):
        range_str = "(" + str(self.interface_range) + ")" if self.is_bus() else ""
        return self.name + " : " + self.interface_type + range_str + " := " + self.default_val


class VHDLControlInput:
    port = Port.default()

    polarity = PolarityType.INVALID

    def __init__(self, port, pol):
        self.port = port
        self.polarity = pol

    @staticmethod
    def reverse_polarity(orig):
        if orig == PolarityType.INVALID:
            return orig

        return PolarityType.NEGATIVE if orig == PolarityType.POSITIVE else PolarityType.POSITIVE


class Clock(VHDLControlInput):

    def __init__(self, port, pol):
        super().__init__(port, pol)
        assert port.dir == PortDir.IN

    @classmethod
    def default(cls):
        return cls(Port("name", "in", "port_type", "port_range"), PolarityType.INVALID)

    def __str__(self):

        if self.polarity == PolarityType.POSITIVE:
            polarity_str = "Rising Edge"
        elif self.polarity == PolarityType.NEGATIVE:
            polarity_str = "Falling Edge"
        else:
            polarity_str = "Invalid Polarity"

        return self.port.port_decl_string() + " : " + polarity_str

    def period_name(self):
        return self.port.name + "_period"


class Reset(VHDLControlInput):

    def __init__(self, port, pol):
        super().__init__(port, pol)
        assert port.dir == PortDir.IN

    def __str__(self):

        if self.polarity == PolarityType.POSITIVE:
            polarity_str = "Active High"
        elif self.polarity == PolarityType.NEGATIVE:
            polarity_str = "Active Low"
        else:
            polarity_str = "Invalid Polarity"

        return self.port.port_decl_string() + " : " + polarity_str


if __name__ == '__main__':
    parse_vhdl(sys.argv[1:])
