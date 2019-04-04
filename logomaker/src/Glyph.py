from matplotlib.textpath import TextPath
from matplotlib.patches import PathPatch
from matplotlib.transforms import Affine2D, Bbox
from matplotlib.font_manager import FontManager, FontProperties
from matplotlib.colors import to_rgb
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from logomaker.src.error_handling import check, handle_errors
import matplotlib.cm
import numpy as np

# Create global font manager instance. This takes a second or two
font_manager = FontManager()


def list_font_names():
    """
    Returns a list of valid font_name options for use in Glyph or
    Logo constructors.

    parameters
    ----------
    None.

    returns
    -------
    fontnames: (list)
        List of valid font_name names. This will vary from system to system.

    """
    fontnames_dict = dict([(f.name, f.fname) for f in font_manager.ttflist])
    fontnames = list(fontnames_dict.keys())
    fontnames.append('sans')  # This always exists
    fontnames.sort()
    return fontnames


class Glyph:
    """
    A Glyph represents a character, drawn on a specified axes at a specified
    position, rendered using specified styling such as color and font_name.

    attributes
    ----------

    p: (number)
        x-coordinate value on which to center the Glyph.

    c: (str)
        The character represented by the Glyph.

    floor: (number)
        y-coordinate value where the bottom of the Glyph extends to.
        Must be < ceiling.

    ceiling: (number)
        y-coordinate value where the top of the Glyph extends to.
        Must be > floor.

    ax: (matplotlib Axes object)
        The axes object on which to draw the Glyph.

    width: (number > 0)
        x-coordinate span of the Glyph.

    vpad: (number in [0,1])
        Amount of whitespace to leave within the Glyph bounding box above
        and below the actual Glyph. Specifically, in a glyph with
        height h = ceiling-floor, a margin of size h*vpad/2 will be left blank
        both above and below the rendered character.

    font_name: (str)
        The name of the font to use when rendering the Glyph. This is
        the value passed as the 'family' parameter when calling the
        matplotlib.font_manager.FontProperties constructor.

    font_weight: (str or number)
        The font weight to use when rendering the Glyph. Specifically, this is
        the value passed as the 'weight' parameter in the
        matplotlib.font_manager.FontProperties constructor.
        From matplotlib documentation: "weight: A numeric
        value in the range 0-1000 or one of 'ultralight', 'light',
        'normal', 'regular', 'book', 'medium', 'roman', 'semibold',
        'demibold', 'demi', 'bold', 'heavy', 'extra bold', 'black'."

    color: (matplotlib color)
        Color to use for Glyph face.

    edgecolor: (matplotlib color)
        Color to use for Glyph edge.

    edgewidth: (number >= 0)
        Width of Glyph edge.

    dont_stretch_more_than: (str)
        This parameter limits the amount that a character will be
        horizontally stretched when rendering the Glyph. Specifying a
        wide character such as 'W' corresponds to less potential stretching,
        while specifying a narrow character such as '.' corresponds to more
        stretching.

    flip: (bool)
        If True, the Glyph will be rendered upside down.

    mirror: (bool)
        If True, a mirror image of the Glyph will be rendered.

    zorder: (number)
        Placement of Glyph within the z-stack of ax.

    alpha: (number in [0,1])
        Opacity of the rendered Glyph.

    draw_now: (bool)
        If True, the Glyph is rendered immediately after it is specified.
        Set to False if you wish to change the properties of this Glyph
        after initial specification and before rendering.
    """

    @handle_errors
    def __init__(self,
                 p,
                 c,
                 floor,
                 ceiling,
                 ax=None,
                 width=0.95,
                 vpad=0.00,
                 font_name='sans',
                 font_weight='bold',
                 color='gray',
                 edgecolor='black',
                 edgewidth=0.0,
                 dont_stretch_more_than='E',
                 flip=False,
                 mirror=False,
                 zorder=None,
                 alpha=1,
                 draw_now=True):

        # Set attributes
        self.p = p
        self.c = c
        self.floor = floor
        self.ceiling = ceiling
        self.ax = ax
        self.width = width
        self.vpad = vpad
        self.flip = flip
        self.mirror = mirror
        self.zorder = zorder
        self.dont_stretch_more_than = dont_stretch_more_than
        self.alpha = alpha
        self.color = to_rgb(color)
        self.edgecolor = edgecolor
        self.edgewidth = edgewidth
        self.font_name = font_name
        self.font_weight = font_weight

        # Check inputs
        self._input_checks()

        # Draw now if requested
        if draw_now:
            self.draw()

    def set_attributes(self, **kwargs):
        """
        Safe way to set the attributes of a Glyph object

        parameters
        ----------
        **kwargs:
            Attributes and their values.
        """
        for key, value in kwargs.items():

            # If key corresponds to a color, convert to rgb
            if key in ('color', 'edgecolor'):
                value = to_rgb(value)

            # Save variable name
            self.__dict__[key] = value

    def draw(self, ax=None):
        """
        Draws Glyph given current parameters.

        parameters
        ----------

        ax: (matplotlib Axes object)
            The axes object on which to draw the Glyph.

        returns
        -------
        None.
        """

        # Make patch
        self.patch = self._make_patch()

        # If user passed ax, use that
        if ax is not None:

            # Check to make sure ax is a matplotlib Axes object
            check(isinstance(ax, Axes),
                  'ax is not a matplotlib Axes object')
            self.ax = ax

        # If ax is not set, set to current axes object
        if self.ax is None:
            self.ax = plt.gca()

        # Draw character
        if self.patch is not None:
            self.ax.add_patch(self.patch)

    def _make_patch(self):
        """
        Returns an appropriately scaled patch object corresponding to
        the Glyph. Note: Does not add this patch to an axes object;
        that is done by draw().
        """

        # Set height
        height = self.ceiling - self.floor

        # If height is zero, just return none
        if height == 0.0:
            return None

        # Set bounding box for character,
        # leaving requested amount of padding above and below the character
        char_xmin = self.p - self.width / 2.0
        char_ymin = self.floor + self.vpad * height / 2.0
        char_width = self.width
        char_height = height - self.vpad * height
        bbox = Bbox.from_bounds(char_xmin,
                                char_ymin,
                                char_width,
                                char_height)

        # Set font properties of Glyph
        font_properties = FontProperties(family=self.font_name,
                                         weight=self.font_weight)

        # Create a path for Glyph that does not yet have the correct
        # position or scaling
        tmp_path = TextPath((0, 0), self.c, size=1,
                            prop=font_properties)

        # Create create a corresponding path for a glyph representing
        # the max stretched character
        msc_path = TextPath((0, 0), self.dont_stretch_more_than, size=1,
                            prop=font_properties)

        # If need to flip char, do it within tmp_path
        if self.flip:
            transformation = Affine2D().scale(sx=1, sy=-1)
            tmp_path = transformation.transform_path(tmp_path)

        # If need to mirror char, do it within tmp_path
        if self.mirror:
            transformation = Affine2D().scale(sx=-11, sy=1)
            tmp_path = transformation.transform_path(tmp_path)

        # Get bounding box for temporary character and max_stretched_character
        tmp_bbox = tmp_path.get_extents()
        msc_bbox = msc_path.get_extents()

        # Compute horizontal stretch factor needed for tmp_path
        hstretch_tmp = bbox.width / tmp_bbox.width

        # Compute horizontal stretch factor needed for msc_path
        hstretch_msc = bbox.width / msc_bbox.width

        # Choose the MINIMUM of these two horizontal stretch factors.
        # This prevents very narrow characters, such as 'I', from being
        # stretched too much.
        hstretch = min(hstretch_tmp, hstretch_msc)

        # Compute the new character width, accounting for the
        # limit placed on the stretching factor
        char_width = hstretch * tmp_bbox.width

        # Compute how much to horizontally shift the character path
        char_shift = (bbox.width - char_width) / 2.0

        # Compute vertical stetch factor needed for tmp_path
        vstretch = bbox.height / tmp_bbox.height

        # THESE ARE THE ESSENTIAL TRANSFORMATIONS
        # 1. First, translate char path so that lower left corner is at origin
        # 2. Then scale char path to desired width and height
        # 3. Finally, translate char path to desired position
        # char_path is the resulting path used for the Glyph
        transformation = Affine2D() \
            .translate(tx=-tmp_bbox.xmin, ty=-tmp_bbox.ymin) \
            .scale(sx=hstretch, sy=vstretch) \
            .translate(tx=bbox.xmin + char_shift, ty=bbox.ymin)
        char_path = transformation.transform_path(tmp_path)

        # Convert char_path to a patch, which can now be drawn on demand
        patch = PathPatch(char_path,
                          facecolor=self.color,
                          zorder=self.zorder,
                          alpha=self.alpha,
                          edgecolor=self.edgecolor,
                          linewidth=self.edgewidth)

        # Return patch representing the Glyph
        return patch

    def _input_checks(self):

        """
        check input parameters in the Logo constructor for correctness
        """

        # check c is of type str
        check(isinstance(self.c, str),
              'type(c) = %s; must be of type str ' %
              type(self.c))

        # validate p
        check(isinstance(int(self.p), (float, int)),
              'type(p) = %s must be a number' % type(self.p))

        # validate floor
        check(isinstance(self.floor, (float, int)),
              'type(floor) = %s must be a number' % type(self.floor))
        self.floor = float(self.floor)

        # validate ceiling
        check(isinstance(self.ceiling, (float, int)),
              'type(ceiling) = %s must be a number' % type(self.ceiling))
        self.ceiling = float(self.ceiling)

        # Check floor < ceiling
        check(self.floor <= self.ceiling,
              'must have floor <= ceiling. Currently, '
              'floor=%f, ceiling=%f' % (self.floor, self.ceiling))

        # Check ax
        check((self.ax is None) or isinstance(self.ax, Axes),
              'ax must be either a matplotlib Axes object or None.')

        # check that flip is a boolean
        check(isinstance(self.flip, (bool, np.bool_)),
              'type(flip) = %s; must be of type bool ' % type(self.flip))
        self.flip = bool(self.flip)

        # check that mirror is a boolean
        check(isinstance(self.mirror, (bool, np.bool_)),
              'type(mirror) = %s; must be of type bool ' % type(self.mirror))
        self.mirror = bool(self.mirror)

        # Check that edgewidth is a number
        check(isinstance(self.edgewidth, (float, int)),
              'type(edgewidth) = %s must be a number' % type(self.edgewidth))
        self.edgewidth = float(self.edgewidth)

        # Check that edgewidth is nonnegative
        check(self.edgewidth >= 0,
              ' edgewidth must be >= 0; is %f' % self.edgewidth)

        # Check alpha is a number
        check(isinstance(self.alpha, (float, int)),
              'type(alpha) = %s must be a number' % type(self.alpha))
        self.alpha = float(self.alpha)

        # Check 0 <= alpha <= 1.0
        check(0 <= self.alpha <= 1.0,
              'alpha must be between 0.0 and 1.0 (inclusive)')

        # check dont_stretch_more_than is of type str
        check(isinstance(self.dont_stretch_more_than, str),
              'type(dont_stretch_more_than) = %s; must be of type str ' %
              type(self.dont_stretch_more_than))

        # check that dont_stretch_more_than is a single character
        check(len(self.dont_stretch_more_than)==1,
              'dont_stretch_more_than must have length 1; '
              'currently len(dont_stretch_more_than)=%d' %
              len(self.dont_stretch_more_than))

        ################# END OF CODE REVIEW ###########################

        # check that color scheme is valid
        valid_color_strings = list(matplotlib.cm.cmap_d.keys())
        valid_color_strings.extend(['classic', 'grays', 'base_paring', 'hydrophobicity', 'chemistry', 'charge'])

        if self.color is not None:

            # if color scheme is specified as a string, check that string message maps
            # to a valid matplotlib color scheme

            if type(self.color) == str:

                # get allowed list of matplotlib color schemes
                check(self.color in valid_color_strings,
                      # 'color_scheme = %s; must be in %s' % (self.color_scheme, str(valid_color_strings)))
                      'color_scheme = %s; is an invalid color scheme. Valid choices include classic, chemistry, grays. '
                      'A full list of valid color schemes can be found by '
                      'printing list(matplotlib.cm.cmap_d.keys()). ' % self.color)

            # otherwise limit the allowed types to tuples, lists, dicts
            else:
                check(isinstance(self.color,(tuple,list,dict)),
                      'type(color_scheme) = %s; must be of type (tuple,list,dict) ' % type(self.color))

                # check that RGB values are between 0 and 1 is
                # color_scheme is a list or tuple

                if type(self.color) == list or type(self.color) == tuple:

                    check(all(i <= 1.0 for i in self.color),
                          'Values of color_scheme array must be between 0 and 1')

                    check(all(i >= 0.0 for i in self.color),
                          'Values of color_scheme array must be between 0 and 1')

        # validate edgecolor
        check(self.edgecolor in list(matplotlib.colors.cnames.keys()),
              # 'color_scheme = %s; must be in %s' % (self.color_scheme, str(valid_color_strings)))
              'edgecolor = %s; is an invalid color scheme. Valid choices include blue, black, silver. '
              'A full list of valid color schemes can be found by '
              'printing list(matplotlib.color_scheme.cnames.keys()). ' % self.edgecolor)

        # validate width
        check(isinstance(self.width, (float, int)),
              'type(width) = %s; must be of type float or int ' % type(self.width))

        check(self.width >= 0, "width = %d must be greater than 0 " % self.width)

        # validate vpad
        check(isinstance(self.vpad, (float, int)),
              'type(vpad) = %s; must be of type float or int ' % type(self.vpad))

        check(self.vpad >= 0, "vpad = %d must be greater than 0 " % self.vpad)

        # validate zorder
        if(self.zorder is not None):
            check(isinstance(self.zorder, int),
                  'type(zorder) = %s; must be of type or int ' % type(self.zorder))

        # validate font_name
        check(isinstance(self.font_name, str),
              'type(font_name) = %s must be of type str' % type(self.font_name))

        check(self.font_name in list_font_names(),
              'Invalid choice for font_name. For a list of valid choices, please call logomaker.list_font_names().')

        check(isinstance(self.font_weight,(str,int)), 'type(font_weight) = %s  should either be a string or an int'%(type(self.font_weight)))

        if(type(self.font_weight)==str):
            valid_font_weight_strings = [ 'ultralight', 'light','normal', 'regular', 'book',
                                          'medium', 'roman', 'semibold', 'demibold', 'demi',
                                          'bold', 'heavy', 'extra bold', 'black']
            check(self.font_weight in valid_font_weight_strings, 'font must be one of %s'%valid_font_weight_strings)

        elif(type(self.font_weight)==int):
            check(self.font_weight>=0 and self.font_weight<=1000, 'font_weight must be in range [0,1000]')

