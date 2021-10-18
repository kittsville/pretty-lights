import web

class Color:

    def __init__(self, hue, sat, lum):
        self.hue = hue
        self.sat = sat
        self.lum = lum

    def toList(self):
        return [
         self.hue, self.sat, self.lum]

    @staticmethod
    def fromDict(params):
        hue = getValue(params, 'hue')
        sat = getValue(params, 'sat')
        lum = getValue(params, 'lum')
        return Color(hue, sat, lum)


def getValue(params, name):
    if name not in params:
        raise web.badrequest(f'Missing param "{name}" from colour config')
    try:
        value = int(params[name])
    except ValueError:
        raise web.badrequest(f"{name} should be an integer, given {params[name]}")

    if value < 0 or value > 255:
        raise web.badrequest(f"{name} should be 0 <= x <= 255, given {value}")
    return value


def generateLedColumns(colors, led_columns):
    if len(colors) > len(led_columns):
        raise web.badrequest(f"Too many colours given, LED lights only have {len(led_columns)} columns")
    else:
        num_color_columns = int(len(led_columns) / len(colors))
        remainder = len(led_columns) % len(colors)
    led_data = []
    for i, color in enumerate(colors):
        num_leds_in_color_column = sum(led_columns[i + remainder:i + remainder + num_color_columns])
        if i == 0:
            num_leds_in_color_column += sum(led_columns[i:i + remainder])
        column_led_data = color.toList() * num_leds_in_color_column
        led_data.extend(column_led_data)

    return led_data


def generateLedBlocks(colors, led_columns, multiplier):
    if len(colors) * multiplier > sum(led_columns):
        raise web.badrequest(f"Multiplier {multiplier} and given colors {len(colors)} greater than number of LEDs {sum(led_columns)}")
    led_data = []
    while len(led_data) < sum(led_columns) * 3:
        for color in colors:
            color_block_led_data = color.toList() * multiplier
            led_data.extend(color_block_led_data)

    led_data[0:(sum(led_columns) - 1) * 3]
    return led_data
