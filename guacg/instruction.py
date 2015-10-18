import json

from guacamole.instruction import GuacamoleInstruction, ARG_SEP


GUACG_PREFIX = '5.guacg'
GUACG_API_OPCODE = 'api'


class GuacgInstruction(GuacamoleInstruction):
    """
    GuacG custom instruction.
    """

    def __init__(self, opcode, *args, **kwargs):
        """
        Initialize custom instruction with proper parsing.

        Normal GuacgInstruction should expect:
            - opcode
            - args: expected json string or dict

        API GuacgInstruction should expect:
            - opcode: 'api'
            - args:
                - '{api_name}'
                - json string or dict
        """
        # Loaded json args rather than normal `self.args` list.
        self.json_args = {}

        # API to be called. Future!
        self.api = None

        # self.args and self.opcode should be ready!
        super(GuacgInstruction, self).__init__(opcode, *args, **kwargs)

        # Get self.json_args and self.api if applicable.
        self.parse()

    @staticmethod
    def is_valid(instruction):
        """
        Checks if instruction string is a valid custom instruction.

        :param instruction: instruction string.

        :return: True if valid, False otherwise.
        """
        if instruction and instruction.startswith(GUACG_PREFIX):
            return True

        return False

    @classmethod
    def load(cls, instruction):
        """
        Load custom instruction.

        :param instruction: Custom instruction string.

        :return: GuacgInstruction()
        """
        if not GuacgInstruction.is_valid(instruction):
            # @TODO: Add custom exceptions.
            raise RuntimeError('Invalid GuacG instruction.')

        # Remove GuacG prefix
        instruction_str = instruction[len(GUACG_PREFIX + ARG_SEP):]

        return super(GuacgInstruction, cls).load(instruction_str)

    def parse(self):
        """
        Parse json args and set self.json_args dict & self.api if exists.
        Instruction Formats:
            - Normal: args = ['<json_string>']
            - API: opcode='api' and args = ['<api_name>', '<json_string>']
        Note: self.json_args can be loaded from '<json_string>' or dict
        """
        if not self.args:
            return

        def load_json(args):
            if isinstance(args, basestring):
                try:
                    return json.loads(args)
                except:
                    return {}
            elif isinstance(args, dict):
                return args

            return {}

        if self.opcode == GUACG_API_OPCODE:
            # This is an API
            self.api = self.args[0]
            if len(self.args) >= 2:
                self.json_args = load_json(self.args[1])
        else:
            # This is a normal custom instruction
            self.json_args = load_json(self.args[0])

    @staticmethod
    def encode_arg(arg):
        """
        Encode argument to be sent in a valid GuacamoleInstruction.
        Overriden to make sure dict arg is converted to valid json string.

        example:
        >> arg = encode_arg({'arg':'1'})
        >> arg == '12.{"arg": "1"}'
        >> True

        :param arg: arg string.

        :return: str
        """
        if isinstance(arg, dict):
            arg = json.dumps(arg)

        return GuacamoleInstruction.encode_arg(arg)

    def encode(self):
        """
        Prepare the *custom* instruction to be sent over the wire.

        :return: str
        """
        instruction_str = super(GuacgInstruction, self).encode()

        # Make sure GUACG_PREFIX is prepended to our instruction string
        instruction_str = GUACG_PREFIX + ARG_SEP + instruction_str

        return '%s' % instruction_str
