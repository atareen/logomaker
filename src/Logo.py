from __future__ import division
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.colors import to_rgb, to_rgba
import matplotlib.cm
import pdb

print('PRINTING FROM LOGO.PY ON RTD')

# Import stuff from logomaker
from latest.src.Glyph import Glyph
from latest.src import color as lm_color
from latest.src.validate import validate_matrix, validate_probability_mat
import latest.src.validate as validate
from latest import ControlledError, check, handle_errors

chars_to_colors_dict = {
    tuple('ACGT'): 'classic',
    tuple('ACGU'): 'classic',
    tuple('ACDEFGHIKLMNPQRSTVWY'): 'hydrophobicity',
}


class Logo:
    """
    Logo represents a basic logo, drawn on a specified axes object
    using a specified matrix.

    attributes
    ----------

    matrix: (pd.DataFrame)
        A matrix specifying character heights and positions. Note that \n
        positions index rows while characters index columns.

    colors: (color scheme)
        Face color of logo characters. Default 'gray'. Here and in \n
        what follows a variable of type 'color' can take a variety of value
        types. \n
         - (str) A Logomaker color scheme in which the color is determined \n
             by the specific character being drawn. Options are, \n
             + For DNA/RNA: 'classic', 'grays', 'base_paring'. \n
             + For protein: 'hydrophobicity', 'chemistry', 'charge'. \n
         - (str) A built-in matplotlib color name  such as 'k' or 'tomato' \n
         - (str) A built-in matplotlib colormap name such as  'viridis' or \n
             'Purples'. In this case, the color within the colormap will \n
             depend on the character being drawn. \n
         - (list) An RGB color (3 floats in interval [0,1]) or RGBA color \n
             (4 floats in interval [0,1]). \n
         - (dict) A dictionary mapping of characters to colors, in which \n
             case the color will depend  on the character being drawn. \n
             E.g., {'A': 'green','C': [ 0.,  0.,  1.], 'G': 'y', \n
             'T': [ 1.,  0.,  0.,  0.5]} \n

    font_name: (str)
        The 'font_name' parameter to pass to FontProperties() \n when creating
        Glyphs.

    stack_order: (str)
        Must be 'big_on_top', 'small_on_top', or 'fixed. If 'big_on_top', \n
        stack glyphs away from x-axis in order of increasing absolute value. \n
        If 'small_on_top', stack glyphs away from x-axis in order of \n
        decreasing absolute value. If 'fixed', stack glyphs from top to bottom \n
        in the order that characters appear in the data frame. If 'flipped', \n
        stack glyphs in the opposite order as 'fixed'. \n

    negate_values: (bool)
        If True, all values in matrix are multiplied by -1. This can be \n
        useful when illustrating negative energy values in an energy matrix. \n

    center_values: (bool)
        If True, the stack of characters at each position will be centered \n
        around zero. This is accomplished by subtracting the mean value \n
        in each row of the matrix from each element in that row. \n

    baseline_width: (float >= 0.0)
        Width of the baseline.

    flip_below: (bool)
        If True, glyphs below the x-axis (which correspond to negative \n
        values in the matrix) will be flipped upside down. \n

    shade_below: (float in [0,1])
        The amount of shading underneath x-axis. \n

    fade_below: (float in [0,1])
        The amount of fading underneath x-axis. \n

    vsep: (float > 0)
        Amount of whitespace to leave between rendered glyphs. Unlike vpad, \n
        vsep is NOT relative to glyph height. The vsep-sized margin between \n
        glyphs on either side of the x-axis will always be centered on the \n
        x-axis.

    zorder: (int >=0)
        The order in which things are drawn.

    figsize: (number, number):
        The default figure size for logos; only needed if ax is not supplied.

    ax: (matplotlib Axes object)
        The axes object on which to draw the logo.

    draw_now: (bool)
        If True, the logo is rendered immediately after it is specified. \n
        Set to False if you wish to change the properties of any glyphs \n
        after initial specification, e.g. by running \n
        Logo.highlight_sequence().

    **kwargs:
        Additional key word arguments to send to the Glyph constructor.
    """

    @handle_errors
    def __init__(self,
                 df,
                 colors=None,
                 font_name='sans',
                 stack_order='big_on_top',
                 negate_values=False,
                 center_values=False,
                 baseline_width=0.5,
                 flip_below=True,
                 shade_below=0.0,
                 fade_below=0.0,
                 vsep=0.0,
                 zorder=0,
                 figsize=(10, 2.5),
                 ax=None,
                 draw_now=True,
                 **kwargs):

        # set class attributes
        self.df = df
        self.colors = colors
        self.font_name = font_name
        self.stack_order = stack_order
        self.negate_values = negate_values
        self.center_values = center_values
        self.baseline_width = baseline_width
        self.flip_below = flip_below
        self.shade_below = shade_below
        self.fade_below = fade_below
        self.vsep = vsep
        self.zorder = zorder
        self.figsize = figsize
        self.ax = ax
        self.draw_now = draw_now

        # perform input checks to validate attributes
        self._input_checks()

        # Compute length
        self.L = len(self.df)

        # Get list of characters
        self.cs = np.array([str(c) for c in self.df.columns])
        self.C = len(self.cs)

        # Get list of positions
        self.ps = np.array([int(p) for p in self.df.index])

        # Set colors by identifying default or otherwise setting to gray
        if colors is None:
            key = tuple(self.cs)
            colors = chars_to_colors_dict.get(key,'gray')
        self.colors = colors

        # Save other attributes
        self.ax = ax
        self.negate_values = bool(negate_values)
        self.center_values = center_values
        self.flip_below = flip_below
        self.vsep = vsep
        self.zorder = zorder
        self.figsize = tuple(figsize)
        self.glyph_kwargs = kwargs

        # Note: Logo does NOT expect df to change after it is passed
        # to the constructor. But one can change character attributes
        # before drawing.

        # Set flag for whether Logo has been drawn
        self.has_been_drawn = False

        # Negate values if requested
        if self.negate_values:
            self.df = -self.df

        # Fill NaN values of matrix_df with zero
        if self.center_values:
            self.df.loc[:, :] = self.df.values - \
                                self.df.values.mean(axis=1)[:, np.newaxis]

        # Compute color dictionary
        self.rgba_dict = lm_color.get_color_dict(
                                    color_scheme=self.colors,
                                    chars=self.cs,
                                    alpha=1)

        # Compute characters.
        self._compute_glyphs()

        # Draw now if requested
        if draw_now:
            self.draw()

        # Style glyphs below x-axis
        self.style_glyphs_below(shade=self.shade_below,
                                fade=self.fade_below,
                                draw_now=self.draw_now)

    def _input_checks(self):

        """
        check input parameters in the Logo constructor for correctness
        """

        # Validate dataframe
        validate_matrix(self.df)

        # check that negate_values is a boolean
        check(isinstance(self.negate_values, bool),
              'type(negate_values) = %s; must be of type bool ' % type(self.negate_values))

        # check that center_values is a boolean
        check(isinstance(self.center_values, bool),
              'type(center_values) = %s; must be of type bool ' % type(self.center_values))

        # check that color scheme is valid
        if self.colors is not None:

            # if color scheme is specified as a string, check that string value maps
            # to a valid matplotlib color scheme

            if type(self.colors) == str:

                # get allowed list of matplotlib color schemes

                valid_color_strings = list(matplotlib.cm.cmap_d.keys())
                valid_color_strings.extend(['classic','grays', 'base_paring','hydrophobicity', 'chemistry', 'charge'])

                check(self.colors in valid_color_strings,
                      # 'colors = %s; must be in %s' % (self.colors, str(valid_color_strings)))
                      'colors = %s; is an invalid color scheme. Valid choices include classic, chemistry, grays. '
                      'A full list of valid color schemes can be found by '
                      'printing list(matplotlib.cm.cmap_d.keys()). ' % self.colors)

            # otherwise limit the allowed types to tuples, lists, dicts
            else:
                check(isinstance(self.colors,(tuple,list,dict)),
                      'type(colors) = %s; must be of type (tuple,list,dict) ' % type(self.colors))

                # check that RGB values are between 0 and 1 is
                # colors is a list or tuple

                if type(self.colors) == list or type(self.colors) == tuple:

                    check(all(i <= 1.0 for i in self.colors),
                          'Values of colors array must be between 0 and 1')

                    check(all(i >= 0.0 for i in self.colors),
                          'Values of colors array must be between 0 and 1')

        # check that stack_order is valid
        check(self.stack_order in {'big_on_top', 'small_on_top', 'fixed', 'flipped'},
              'stack_order = %s; must be "big_on_top", "small_on_top", "fixed", "flipped".' % self.stack_order)

        # check that flip_below is a boolean
        check(isinstance(self.flip_below, bool),
            'type(flip_below) = %s; must be of type bool ' % type(self.flip_below))

        # validate vsep
        check(isinstance(self.vsep, (float, int)),
              'type(vsep) = %s; must be of type or int ' % type(self.vsep))

        check(self.vsep >= 0, "vsep = %d must be greater than 0 " % self.vsep)

        # validate zorder
        check(isinstance(self.zorder, int),
              'type(zorder) = %s; must be of type or int ' % type(self.zorder))

        check(self.zorder >= 0, "zorder = %d must be greater than 0 " % self.zorder)

        # validate figsize
        check(isinstance(self.figsize, (tuple, list)),
              'type(figsize) = %s; must be of type (tuple,list) ' % type(self.figsize))

        check(len(self.figsize)==2, 'The figsize array must have two elements')

        check(all(i > 0 for i in self.figsize),
              'Values of figsize array must be > 0')

        # validate ax. Need to go over this in code review
        #check(isinstance(self.ax,(None,matplotlib.axes._base._AxesBase)),
              #'ax needs to be None or a valid matplotlib axis object')

        # check that draw_now is a boolean
        check(isinstance(self.draw_now, bool),
              'type(draw_now) = %s; must be of type bool ' % type(self.draw_now))

        ### after this point, the function will check inputs that are not part of the constructor. ###
        ### so checking the existence of an attribute will become necessary. ###

        # validate fade
        if(hasattr(self,'fade')):
            check(isinstance(self.fade,(float,int)), 'type(fade) = %s must be of type float' % type(self.fade))

            # ensure that fade is between 0 and 1
            check(self.fade <= 1.0 and self.fade >= 0, 'fade must be between 0 and 1')

        # validate shade
        if (hasattr(self, 'shade')):
            check(isinstance(self.shade, (float, int)), 'type(shade) = %s must be of type float' % type(self.shade))

            # ensure that fade is between 0 and 1
            check(self.shade <= 1.0 and self.shade >= 0, 'shade must be between 0 and 1')

        if (hasattr(self, 'sequence')):
            check(isinstance(self.sequence, str), 'type(sequence) = %s must be of type str' % type(self.sequence))

        # validate p
        if (hasattr(self, 'p')):
            check(isinstance(self.p, int), 'type(p) = %s must be of type int' % type(self.p))

        # validate c
        if (hasattr(self, 'c')):
            check(isinstance(self.c, str), 'type(c) = %s must be of type str' % type(self.c))

        # validate spines
        if(hasattr(self,'spines')):
            check(isinstance(self.spines, (tuple, list)),
                  'type(spines) = %s; must be of type (tuple,list) ' % type(self.spines))

            # check if items of spines are valid if tuple
            valid_spines_tuple = ('top', 'bottom', 'left', 'right')
            if(isinstance(self.spines,tuple)):

                # ensure elements of spines are valid:
                # the following code checks if spines is a subset of a the valid spines choices.
                check(set(self.spines) <= set(valid_spines_tuple),
                      'choice of spine not valid, valid choices include: '+str(valid_spines_tuple))

            # check if items of spines are valid if list
            valid_spines_list = ['top', 'bottom', 'left', 'right']

            # ensure elements of spines are valid:
            # the following code checks if spines is a subset of a the valid spines choices.
            if (isinstance(self.spines, list)):
                check(set(self.spines) <= set(valid_spines_list),
                      'choice of spine not valid, valid choices include:'+str(valid_spines_list))

        # validate visible
        if(hasattr(self,'visible')):
            check(isinstance(self.visible,bool),
                  'type(visible) = %s; must be of type bool ' % type(self.visible))

        # validate linewidth
        if(hasattr(self,'linewidth')):

            check(isinstance(self.linewidth,(float,int)),
                  'type(linewidth) = %s; must be of type float ' % type(self.linewidth))

            check(self.linewidth>=0,'linewidth must be >= 0')

        # validate bounds
        if(hasattr(self,'bounds')):

            if self.bounds is not None :
                # check that bounds are of valid type
                bounds_types = (list, tuple, np.ndarray)
                check(isinstance(self.bounds, bounds_types),
                      'type(bounds) = %s; must be one of %s' % (type(self.bounds), bounds_types))

                # bounds has right length
                check(len(self.bounds) == 2,
                      'len(bounds) = %d; must be %d' %(len(self.bounds), 2))

                # ensure that elements of bounds are numbers
                check(isinstance(self.bounds[0],(float,int)) & isinstance(self.bounds[1],(float,int)),
                      'bounds = %s; entries must be numbers' %repr(self.bounds))

                # bounds entries must be sorted
                check(self.bounds[0] < self.bounds[1],
                      'bounds = %s; entries must be sorted' %repr(self.bounds))

        # validate anchor
        if(hasattr(self,'anchor')):
            check(isinstance(self.anchor,int),'type(anchor) = %s must be of type int' % type(self.anchor))

        # validate spacing
        if (hasattr(self, 'spacing')):
            check(isinstance(self.spacing, int), 'type(spacing) = %s must be of type int' % type(self.spacing))

            check(self.spacing>0, 'spacing must be > 0')

        # validate fmt
        if(hasattr(self,'fmt')):
            check(isinstance(self.fmt,str),'type(fmt) = %s must be of type str' % type(self.fmt))

        # validate rotation
        if (hasattr(self, 'rotation')):
            check(isinstance(self.rotation, (float, int)),
                      'type(rotation) = %s; must be of type float or int ' % type(self.rotation))


    @handle_errors
    def style_glyphs(self, colors=None, draw_now=True, ax=None, **kwargs):
        """
        Modifies the properties of all glyphs in a logo.

        parameter
        ---------

        colors: (color scheme)
            Color specification for glyphs. See logomaker.Logo for details.

        draw_now: (bool)
            Whether to re-draw modified logo on current Axes.

        ax: (matplotlib Axes object)
            New axes, if any, on which to draw logo if draw_now=True.

        **kwargs:
            Keyword arguments to pass to Glyph.set_attributes()

        returns
        -------
        None
        """

        # set attributes
        self.colors = colors
        self.draw_now = draw_now

        # Update ax if axes are provided by the user.
        self._update_ax(ax)

        self._input_checks()

        # Reset colors if provided
        if colors is not None:
            self.colors = colors

            # the following case represents an error that may occur if a user accidentally runs
            # style glyphs before running the logo constructor. The following check puts out a
            # clean message, no need for stack-trace. hasattr checks if self has attribute cs.
            check(hasattr(self,'cs'), 'Characters entered into style glyphs are None, please ensure'
                                   ' Logo ran correctly before running style_glyphs')

            self.rgba_dict = lm_color.get_color_dict(
                                    color_scheme=self.colors,
                                    chars=self.cs,
                                    alpha=1)

        # Record zorder if this is provided
        if 'zorder' in kwargs.keys():
            self.zorder = kwargs['zorder']

        # Modify all glyphs
        for g in self.glyph_list:

            # Set each glyph attribute
            g.set_attributes(**kwargs)

            # If colors is not None, this should override
            if colors is not None:
                this_color = self.rgba_dict[g.c][:3]
                g.set_attributes(color=this_color)

        # Draw now if requested
        if draw_now:
            self.draw()


    def fade_glyphs_in_probability_logo(self,
                                        v_alpha0=0,
                                        v_alpha1=1,
                                        draw_now=True,
                                        ax=None):

        """
        Fades glyphs in probability logo according to value

        parameter
        ---------

        v_alpha0 / v_alpha1: (number in [0,1])
            Matrix values marking alpha=0 and alpha=1

        draw_now: (bool)
            Whether to readraw modified logo on current Axes.

        ax: (matplotlib Axes object)
            New axes, if any, on which to draw logo if draw_now=True.

        returns
        -------
        None
         """

        # Update ax if axes are provided by the user.
        self._update_ax(ax)

        # Make sure matrix is a probability matrix
        self.df = validate_probability_mat(self.df)

        # Iterate over all positions and characters
        for p in self.ps:
            for c in self.cs:

                # Grab both glyph and value
                v = self.df.loc[p, c]
                g = self.glyph_df.loc[p, c]

                # Compute new alpha
                if v <= v_alpha0:
                    alpha = 0
                elif v >= v_alpha1:
                    alpha = 1
                else:
                    alpha = (v - v_alpha0) / (v_alpha1 - v_alpha0)

                # Set glyph attributes
                g.set_attributes(alpha=alpha)

        # Draw now if requested
        if draw_now:
            self.draw()

    @handle_errors
    def style_glyphs_below(self,
                           shade=0.0,
                           fade=0.0,
                           flip=True,
                           draw_now=True,
                           ax=None,
                           **kwargs):

        """
        Modifies the properties of all glyphs below the x-axis in a logo.

        parameter
        ---------

        shade: (float)
            The amount of shading underneath x-axis. Range is [0,1]

        fade: (float)
            The amount of fading underneath x-axis .Range is [0,1]

        flip: (bool)
            If True, the glyph will be rendered flipped upside down.

        ax: (matplotlib Axes object)
            The axes object on which to draw the logo.

        draw_now: (bool)
            If True, the logo is rendered immediately after it is specified.
            Set to False if you wish to change the properties of any glyphs
            after initial specification, e.g. by running
            Logo.highlight_sequence().

        **kwargs:
            Keyword arguments to pass to Glyph.set_attributes()

        returns
        -------
        None
        """

        # set attributes
        self.shade = shade
        self.fade = fade
        self.flip = flip
        self.draw_now = draw_now

        # Update ax if axes are provided by the user.
        self._update_ax(ax)

        # validate inputs
        self._input_checks()

        # the following two checks ensure that the attributes cs and ps exist,
        # this could throw an error in jupyter notebooks if a user ran this function
        # with an incorrectly run Logo object.

        check(hasattr(self, 'cs'), 'Characters entered into are None, please ensure'
                                   ' Logo ran correctly before running style_glyphs_below')

        check(hasattr(self, 'ps'), 'positions entered into are None, please ensure'
                                   ' Logo ran correctly before running style_glyphs_below')

        # Iterate over all positions and characters
        for p in self.ps:
            for c in self.cs:

                # If matrix value is < 0
                v = self.df.loc[p, c]
                if v < 0:

                    #  Get glyph
                    g = self.glyph_df.loc[p, c]

                    # Modify color and alpha
                    color = np.array(g.color) * (1.0 - shade)
                    alpha = g.alpha * (1.0 - fade)

                    # Set glyph attributes
                    g.set_attributes(color=color,
                                     alpha=alpha,
                                     flip=flip,
                                     **kwargs)

        # Draw now if requested
        if draw_now:
            self.draw()

    @handle_errors
    def style_single_glyph(self, p, c, draw_now=False, ax=None, **kwargs):
        """
        Modifies the properties of a component glyph in a logo.

        parameter
        ---------

        p: (number)
            Position of modified glyph. Must index a row in the matrix passed
            to the Logo constructor.

        c: (str)
            Character of modified glyph. Must index a column in the matrix
            passed to the Logo constructor.

        draw_now: (bool)
            Whether to readraw modified logo on current Axes.

        ax: (matplotlib Axes object)
            New axes, if any, on which to draw logo if draw_now=True.

        **kwargs:
            Keyword arguments to pass to Glyph.set_attributes()

        returns
        -------
        None
        """

        # set attributes
        self.p = p
        self.c = c
        self.draw_now = draw_now
        self.ax = ax

        # validate inputs
        self._input_checks()

        # Update ax if axes are provided by the user.
        self._update_ax(ax)

        check(self.p in self.glyph_df.index,'Error: p=%s is not a valid position' % p)
        check(self.c in self.glyph_df.columns,'Error: c=%s is not a valid character' % c)

        # Get glyph from glyph_df
        g = self.glyph_df.loc[p, c]
        g.set_attributes(**kwargs)

        # using true will draw the entire logo one glyph at a time.
        # causes big slow down. I don't if it's good to keep this call here.
        if draw_now:
            self.draw()

    @handle_errors
    def style_glyphs_in_sequence(self,
                                 sequence,
                                 draw_now=True,
                                 ax=None,
                                 **kwargs):
        """
        Highlights a specified sequence by changing the parameters of the
        glyphs at each corresponding position in that sequence. To use this,
        first run constructor with draw_now=False.

        parameters
        ----------
        sequence: (str)
            A string the same length as the logo, specifying which character
            to highlight at each position.

        draw_now: (bool)
            Whether to readraw modified logo on current Axes.

        ax: (matplotlib Axes object)
            New axes, if any, on which to draw logo if draw_now=True.

        **kwargs:
            Keyword arguments to pass to Glyph.set_attributes()

        returns
        -------
        None
        """

        self.sequence = sequence
        self.draw_now = draw_now

        # validate input
        self._input_checks()

        # Update Axes if axes are provided by the user.
        self._update_ax(ax)

        check(len(self.sequence) == self.L,
              'Error: sequence to highlight does not have same length as logo.')

        # For each position in the logo...
        for i, p in enumerate(self.glyph_df.index):

            # Get character to highlight
            c = self.sequence[i]

            # Modify the glyph corresponding character c at position p
            # Only modify if c is a valid character. If not, ignore position
            if c in self.cs:
                self.style_single_glyph(p, c, **kwargs)

        # Draw now
        if draw_now:
            self.draw()

    def highlight_position(self, p, **kwargs):

        """
        ** Can only modify Axes that has already been set. **

        parameters
        ----------
        p: (number)
            Single position to highlight

        **kwargs:
            Other parameters to pass to highlight_position_range()

        returns
        -------
        None
        """

        assert self.has_been_drawn, \
            'Error: Cannot call this function until Log0 has been drawn.'

        self.highlight_position_range(pmin=p, pmax=p, **kwargs)

    def highlight_position_range(self, pmin, pmax,
                                 padding=0.0,
                                 color='yellow',
                                 edgecolor=None,
                                 floor=None,
                                 ceiling=None,
                                 zorder=-2,
                                 **kwargs):
        """
        Highlights multiple positions
        ** Can only modify Axes that has already been set. **

        parameters
        ----------
        pmin: (number)
            Lowest position to highlight.
            
        pmax: (number)
            Highest position to highlight.
            
        padding: (number >= -0,5)
            Amount of padding on either side of highlighted positions to add.
            
        color: (matplotlib color)
            Matplotlib color.
            
        floor: (number)
            Lower-most extent of highlight. If None, is set to Axes ymin.
            
        ceiling: (number)
            Upper-most extent of highlight. If None, is set to Axes ymax.
            
        zorder: (number)
            Placement of highlight rectangle in Axes z-stack.

        **kwargs:
            Other parmeters to pass to highlight_single_position

        returns
        -------
        None
        """

        assert self.has_been_drawn, \
            'Error: Cannot call this function until Log0 has been drawn.'

        # If floor or ceiling have not been specified, using Axes ylims
        ymin, ymax = self.ax.get_ylim()
        if floor is None:
            floor = ymin
        if ceiling is None:
            ceiling = ymax
        assert floor < ceiling, \
            'Error: floor < ceiling not satisfied.'

        # Set coordinates of rectangle
        assert pmin <= pmax, \
            'Error: pmin <= pmax not satisfied.'
        assert padding >= -0.5, \
            'Error: padding >= -0.5 not satisfied'
        x = pmin - .5 - padding
        y = floor
        width = pmax - pmin + 1 + 2*padding
        height = ceiling-floor

        # Draw rectangle
        patch = Rectangle(xy=(x, y),
                          width=width,
                          height=height,
                          facecolor=color,
                          edgecolor=edgecolor,
                          zorder=zorder,
                          **kwargs)
        self.ax.add_patch(patch)

    def draw_baseline(self,
                      zorder=-1,
                      color='black',
                      linewidth=0.5,
                      **kwargs):
        """
        Draws a line along the x-axis.
        ** Can only modify Axes that has already been set. **

        parameters
        ----------

        zorder: (number)
            The z-stacked location where the baseline is drawn

        color: (matplotlib color)
            Color to use for the baseline

        linewidth: (float >= 0)
            Width of the baseline

        **kwargs:
            Additional keyword arguments to be passed to ax.axhline()


        returns
        -------
        None
        """

        assert self.has_been_drawn, \
            'Error: Cannot call this function until Log0 has been drawn.'

        # Render baseline
        self.ax.axhline(zorder=zorder,
                        color=color,
                        linewidth=linewidth,
                        **kwargs)

    @handle_errors
    def style_xticks(self,
                     anchor=0,
                     spacing=1,
                     fmt='%d',
                     rotation=0.0,
                     **kwargs):
        """
        Formats and styles tick marks along the x-axis.
        ** Can only modify Axes that has already been set. **

        parameters
        ----------

        anchor: (int)
            Anchors tick marks at a specific number. Even if this number
            is not within the x-axis limits, it fixes the register for
            tick marks.

        spacing: (int > 0)
            The spacing between adjacent tick marks

        fmt: (str)
            String used to format tick labels.

        rotation: (number)
            Angle, in degrees, with which to draw tick mark labels.

        **kwargs:
            Additional keyword arguments to be passed to ax.set_xticklabels()


        returns
        -------
        None
        """

        # set attributes
        self.anchor = anchor
        self.spacing = spacing
        self.fmt = fmt
        self.rotation = rotation

        # validate input
        self._input_checks()

        if (hasattr(self, 'has_been_drawn')):
            check(self.has_been_drawn == True, 'Error: Cannot call this function until Logo has been drawn.')

        # Get list of positions, ps, that spans all those in matrix_df
        p_min = min(self.ps)
        p_max = max(self.ps)
        ps = np.arange(p_min, p_max+1)

        # Compute and set xticks
        xticks = ps[(ps - anchor) % spacing == 0]
        self.ax.set_xticks(xticks)

        # Compute and set xticklabels
        xticklabels = [fmt % p for p in xticks]
        self.ax.set_xticklabels(xticklabels, rotation=rotation, **kwargs)

    @handle_errors
    def style_spines(self,
                     spines=('top', 'bottom', 'left', 'right'),
                     visible=True,
                     linewidth=1.0,
                     color='black',
                     bounds=None):
        """
        Turns spines on an off.
        ** Can only modify Axes that has already been set. **

        parameters
        ----------

        spines: (tuple of str)
            Specifies which of the four spines to modify. Default lists
            all possible entries.

        visible: (bool)
            Whether or not a spine is drawn.

        color: (matplotlib color)
            Spine color.

        linewidth: (float >= 0)
            Spine width.

        bounds: ([float, float])
            Specifies the upper- and lower-bounds of a spine.

        **kwargs:
            Additional keyword arguments to be passed to ax.axhline()

        returns
        -------
        None
        """

        # set attributes
        self.spines = spines
        self.visible = visible
        self.linewidth = linewidth
        self.color = color
        self.bounds = bounds

        # validate inputs
        self._input_checks()

        if(hasattr(self,'has_been_drawn')):
            check(self.has_been_drawn==True,'Error: Cannot call this function until Logo has been drawn.')

        # Iterate over all spines
        for name, spine in self.ax.spines.items():

            # If name is in the set of spines to modify
            if name in spines:

                # Modify given spine
                spine.set_visible(visible)
                spine.set_color(color)
                spine.set_linewidth(linewidth)

                if bounds is not None:
                    spine.set_bounds(bounds[0], bounds[1])

    def draw(self, ax=None):
        """
        Draws glyphs on the axes object 'ax' provided to the Logo
        constructor

        parameters
        ----------
        None

        returns
        -------
        None
        """

        # Update ax
        self._update_ax(ax)

        # If ax is still None, create figure
        if self.ax is None:
            fig, ax = plt.subplots(1, 1, figsize=self.figsize)
            self.ax = ax

        # Clear previous content from ax
        self.ax.clear()

        # Flag that this logo has not been drawn
        self.has_been_drawn = False

        # Draw each glyph
        for g in self.glyph_list:
            g.draw(self.ax)

        # Flag that this logo has indeed been drawn
        self.has_been_drawn = True

        # Draw baseline
        self.draw_baseline(linewidth=self.baseline_width)

        # Set xlims
        xmin = min([g.p - .5*g.width for g in self.glyph_list])
        xmax = max([g.p + .5*g.width for g in self.glyph_list])
        self.ax.set_xlim([xmin, xmax])

        # Set ylims
        ymin = min([g.floor for g in self.glyph_list])
        ymax = max([g.ceiling for g in self.glyph_list])
        self.ax.set_ylim([ymin, ymax])

    def _update_ax(self, ax):
        """ Reset ax if user has passed a new one."""
        if ax is not None:
            self.ax = ax

    def _compute_glyphs(self):
        """
        Specifies the placement and styling of all glyphs within the logo.
        Note that glyphs can later be changed after this is called but before
        draw() is called.
        """
        # Create a dataframe of glyphs
        glyph_df = pd.DataFrame()
        vsep = self.vsep

        # For each position
        for p in self.ps:

            # Get values at this position
            vs = np.array(self.df.loc[p, :])

            # Sort values and corresponding characters as desired
            if self.stack_order == 'big_on_top':
                ordered_indices = np.argsort(vs)

            elif self.stack_order == 'small_on_top':
                tmp_vs = np.zeros(len(vs))
                tmp_vs[vs != 0] = 1/vs

                ordered_indices = np.argsort(tmp_vs)
            elif self.stack_order == 'fixed':
                ordered_indices = np.array(range(len(vs)))[::-1]

            elif self.stack_order == 'flipped':
                ordered_indices = np.array(range(len(vs)))

            else:
                assert False, 'This should not be possible.'

            # Reorder values and characters
            vs = vs[ordered_indices]
            cs = [str(c) for c in self.cs[ordered_indices]]

            # Set floor
            floor = sum((vs - vsep) * (vs < 0)) + vsep/2.0

            # For each character
            for n, v, c in zip(range(self.C), vs, cs):

                # Set ceiling
                ceiling = floor + abs(v)

                # Set color
                rgba = self.rgba_dict[c]
                this_color = rgba[:3]

                # Set whether to flip character
                flip = (v < 0 and self.flip_below)

                # Create glyph if height is finite
                glyph = Glyph(p, c,
                              ax=self.ax,
                              floor=floor,
                              ceiling=ceiling,
                              color=this_color,
                              flip=flip,
                              draw_now=False,
                              zorder=self.zorder,
                              font_family=self.font_name,
                              **self.glyph_kwargs)

                # Add glyph to glyph_df
                glyph_df.loc[p, c] = glyph

                # Raise floor to current ceiling
                floor = ceiling + vsep

        # Set glyph_df attribute
        self.glyph_df = glyph_df
        self.glyph_list = [g for g in self.glyph_df.values.ravel()
                           if isinstance(g, Glyph)]

