import numpy as np
from matplotlib import pyplot as pp


# Function to get list of axes for plotting
def get_axes(n_axes, ax_label=None, ay_label=None):
    """Generate a set of axes ready for plotting multiple fields or grids.

    Args:
        n_axes int: number of axes to generate.
        ax_label str: label for x axes. Only shown on bottom axes.
        ay_label str: label for y axes. Only shown on left-most axes.

    Returns:
        ``matplotlib.Figure``: figure object.
        list: of ``matplotlib.Axes``: list of individual subplot axes.
    """
    if n_axes > 9:
        pp.rcParams['figure.figsize'] = 12, 16
        fig, axes_array = pp.subplots(4, 3, squeeze=False)
    elif n_axes > 6:
        pp.rcParams['figure.figsize'] = 12, 12
        fig, axes_array = pp.subplots(3, 3, squeeze=False)
    elif n_axes > 4:
        pp.rcParams['figure.figsize'] = 12, 9
        fig, axes_array = pp.subplots(2, 3, squeeze=False)
    elif n_axes > 2:
        pp.rcParams['figure.figsize'] = 12, 9
        fig, axes_array = pp.subplots(2, 2, squeeze=False)
    elif n_axes == 2:
        pp.rcParams['figure.figsize'] = 12, 9
        fig, axes_array = pp.subplots(1, 2, squeeze=False)
    else:  # One feed only
        fig, axes_array = pp.subplots(1, 1, squeeze=False)

    # Turn off all axes, and then turn them on when we use them
    for ax in axes_array.flatten():
        ax.axis('off')
    # Set X label for the bottom row of plots
    for ax in axes_array[-1, :]:
        ax.set_xlabel(ax_label)
    # Set Y label for the first column of plots
    for ax in axes_array[:, 0]:
        ax.set_ylabel(ay_label)
    # Turn off ticklabels for plots not on bottom row or left column
    try:
        for ax in axes_array[:-1, :].flatten():
            ax.set_xticklabels([])
    except IndexError:
        pass
    try:
        for ax in axes_array[:, 1:].flatten():
            ax.set_yticklabels([])
    except IndexError:
        pass

    axes = axes_array.flatten()

    return fig, axes


def get_max_fields(fields, step, component=0, db=True):
    """Finds the maximum amplitude in the set of fields and return a suitable common limit for plotting all fields.

    Returns the next value equal to n x step above the maximum amplitude found.

    Args:
        fields (list: of :obj:`GraspField`): the set of fields to determine common limits for.
        step (float): Step size to change the limit by.
        component (int): index of the field component to use.
        db (bool): Work in db(amplitude)

    Returns:
        float: limit suitable for plotting all fields."""
    if db:
        limit = -1000.0
    else:
        limit = 0.0

    for field in fields:
        if db:
            data = 20 * np.log10(np.abs(field.field[:, :, component]))
        else:
            data = np.abs(field.field[:, :, component])

        max_data = np.amax(data)
        if not db:
            step = max_data / 10.0
        if max_data > limit:
            limit = step * np.ceil(max_data / step)

    return limit


def plot_amplitude_fields(fields, component, suptitle=None, titles=None, xlabel=None, ylabel=None, vlabel=None,
                          limits=None, db=True, cmap="gist_heat"):
    """Plot all of the fields supplied as subplots in a single figure.

    Args:
        fields (list: of :obj:`GraspField`): set of fields to plot.
        component (int:): field component to plot.
        suptitle (str:): title to use for overall figure.
        titles (list: of str:): titles to use for each field.
        xlabel (str:): x axis label.
        ylabel (str:): y axis label.
        vlabel (str:): colorbar label.
        limits (tuple: of float:): lower and upper limits for color scale. If not given, will default to 0 to max for
                                absolute, ~40 db below maximum for db.
        db (bool:): plot db (or absolute):
        cmap (str:): name of matplotlib cmap to use

    Returns:
        :obj: `matplotlib.Figure`: matplotlib Figure containing the plots.
        """
    fig, axes = get_axes(len(fields), xlabel, ylabel)

    if limits:
        v_min = limits[0]
        v_max = limits[1]
    else:
        step = 2
        v_max = get_max_fields(fields, step, component, db)
        if db:
            v_min = v_max - 40.0
        else:
            v_min = 0.0

    for f, field in enumerate(fields):
        ax = axes[f]
        ax.axis('on')

        if db:
            im = ax.imshow(20 * np.log10(np.abs(field.field[:, :, component])),
                           cmap=cmap, interpolation=None, origin="lower",
                           extent=[field.grid_min_x, field.grid_max_x, field.grid_min_y, field.grid_max_y],
                           vmin=v_min, vmax=v_max)
        else:
            im = ax.imshow((np.abs(field.field[:, :, component])),
                           cmap=cmap, interpolation=None, origin="lower",
                           extent=[field.grid_min_x, field.grid_max_x, field.grid_min_y, field.grid_max_y],
                           vmin=v_min, vmax=v_max)
        ax.grid(color='w', linestyle='--')
        if titles:
            ax.set_title(titles[f])

    fig.suplots_adjust(right=0.85)
    cbar_ax = fig.add_axes([0.87, 0.13, 0.02, 0.7])
    cbar = fig.colorbar(im, cax=cbar_ax)
    cbar.ax.set_ylabel(vlabel)

    fig.suptitle(suptitle)

    return fig


def plot_amplitude_grids(grids, field, component, suptitle=None, titles=None, xlabel=None, ylabel=None, vlabel=None,
                         limits=None, db=True, cmap="gist_heat"):
    """Plot all of the fields supplied as subplots in a single figure.

    Args:
        grids (list: of :obj:`GraspField`): set of grids to plot.
        field (int:): index of field from each grid to plot.
        component (int:): field component to plot.
        suptitle (str:): title to use for overall figure.
        titles (list: of str:): titles to use for each field.
        xlabel (str:): x axis label.
        ylabel (str:): y axis label.
        vlabel (str:): colorbar label.
        limits (tuple: of float:): lower and upper limits for color scale.
        db (bool:): plot db (or absolute):
        cmap (str:): name of matplotlib cmap to use

    Returns:
        :obj: `matplotlib.Figure`: matplotlib Figure containing the plots.
        """
    fields = []
    for grid in grids:
        fields.append(grid.fields[field])

    return plot_amplitude_fields(fields, component, suptitle, titles, xlabel, ylabel, vlabel, limits, db, cmap)


def plot_phase_fields(fields, component, suptitle=None, titles=None, xlabel=None, ylabel=None, vlabel=None,
                      limits=None, cmap="jet"):
    """Plot the phase of all of the fields supplied as subplots in a single figure.

    Args:
        fields (list: of :obj:`GraspField`): set of fields to plot.
        component (int:): field component to plot.
        suptitle (str:): title to use for overall figure.
        titles (list: of str:): titles to use for each field.
        xlabel (str:): x axis label.
        ylabel (str:): y axis label.
        vlabel (str:): colorbar label.
        limits (tuple: of float:): lower and upper limits for color scale. If not given, plots will be from -180 to 180
        db (bool:): plot db (or absolute):
        cmap (str:): name of matplotlib cmap to use

    Returns:
        :obj: `matplotlib.Figure`: matplotlib Figure containing the plots.
        """
    fig, axes = get_axes(len(fields), xlabel, ylabel)

    if limits:
        v_min = limits[0]
        v_max = limits[1]
    else:
        v_min = -180.0
        v_max = 180.0

    for f, field in enumerate(fields):
        ax = axes[f]
        ax.axis('on')

        im = ax.imshow(np.angle(field.field[:, :, component], deg=True),
                       cmap=cmap, interpolation=None, origin="lower",
                       extent=[field.grid_min_x, field.grid_max_x, field.grid_min_y, field.grid_max_y],
                       vmin=v_min, vmax=v_max)
        ax.grid(color='w', linestyle='--')
        if titles:
            ax.set_title(titles[f])

    fig.suplots_adjust(right=0.85)
    cbar_ax = fig.add_axes([0.87, 0.13, 0.02, 0.7])
    cbar = fig.colorbar(im, cax=cbar_ax)
    cbar.ax.set_ylabel(vlabel)

    fig.suptitle(suptitle)

    return fig


def plot_phase_grids(grids, field, component, suptitle=None, titles=None, xlabel=None, ylabel=None, vlabel=None,
                     limits=None, cmap="jet"):
    """Plot the phase of all of the grids supplied as subplots in a single figure.

    Args:
        grids (list: of :obj:`GraspField`): set of fields to plot.
        field (int:): index of field from each grid to plot.
        component (int:): field component to plot.
        suptitle (str:): title to use for overall figure.
        titles (list: of str:): titles to use for each field.
        xlabel (str:): x axis label.
        ylabel (str:): y axis label.
        vlabel (str:): colorbar label.
        limits (tuple: of float:): lower and upper limits for color scale. If not given, plots will be from -180 to 180
        db (bool:): plot db (or absolute):
        cmap (str:): name of matplotlib cmap to use

    Returns:
        :obj: `matplotlib.Figure`: matplotlib Figure containing the plots.
        """
    fields = []
    for grid in grids:
        fields.append(grid.fields[field])

    return plot_phase_fields(fields, component, suptitle, titles, xlabel, ylabel, vlabel, limits, cmap)
