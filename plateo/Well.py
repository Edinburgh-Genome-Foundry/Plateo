from box import Box

class TransferError(ValueError):
    pass

class WellContent:
    """Class to represent the volume and quantities of a well.

    Having the well content represented as a separate object makes it possible
    to have several wells share the same content, e.g. in throughs.
    """

    def __init__(self, quantities=None, volume=0):
        if quantities is None:
            quantities = {}
        self.volume = volume
        self.quantities = Box(quantities)

    def concentration(self, component=None, default=0):
        if self.quantities == {}:
            return default
        if self.volume == 0:
            return default
        if component is None:
            component = list(self.quantities.keys())[0]
        if component not in self.quantities:
            return default
        return 1.0 * self.quantities[component] / self.volume

    def to_dict(self):
        """Return a dict {volume: 0.0001, quantities: {...:...}}"""
        return {
            "volume": self.volume,
            "quantities": self.quantities
        }

    def make_empty(self):
        self.volume = 0
        self.quantities = Box({})

    def components_as_string(self, separator=" "):
        """Return a string representation of what's in the well mix"""
        return separator.join(sorted(self.quantities.keys()))

class Well:
    """Generic class for a well.

    Parameters
    ----------

    plate
      The plate on which the well is located

    row
      The well's row (a number, starting from 0)

    column
      The well's column (a number, starting from 0)

    name
      The well's name, for instance "A1"

    data
      A dictionnary storing data on the well, used in algorithms and reports.


    """
    capacity = None

    def __init__(self, plate, row, column, name, data=None):
        self.plate = plate
        self.row = row
        self.column = column
        self.name = name
        self.data = Box({} if data is None else data)
        self.sources = []
        self.content = WellContent()

    @property
    def volume(self):
        return self.content.volume

    def iterate_sources_tree(self):
        for source in self.sources:
            if isinstance(source, Well):
                for parent in source.iterate_sources_tree():
                    yield parent
            else:
                yield source
        yield self

    def transfer_to_other_well(self, destination_well, transfer_volume):
        if self.is_empty:
            raise TransferError(
                "Transfer %s => %s impossible: %s is empty" % (
                 self, destination_well, self))
        factor = float(transfer_volume) / self.volume

        #  pre-check in both source and destination wells that transfers
        #  are valid
        if factor > 1:
            raise TransferError(
                ("Substraction of %.2e L from %s impossible."
                 " Current volume: %.2e L")
                % (transfer_volume, self, self.volume)
            )
        final_destination_volume = destination_well.volume + transfer_volume
        if ((destination_well.capacity is not None) and
           (final_destination_volume > destination_well.capacity)):
            raise TransferError(
                "Transfer of %.2e L from %s to %s brings volume over capacity."
                % (transfer_volume, self, destination_well)
            )

        #  If you arrive here, it means that the transfer is valid, do it.
        quantities_transfered = {
            component: quantity * factor
            for component, quantity in self.content.quantities.items()
        }
        destination_well.add_content(quantities_transfered,
                                     volume=transfer_volume)
        self.subtract_content(quantities_transfered,
                              volume=transfer_volume)
        if self not in destination_well.sources:
            destination_well.sources.append(self)

    def add_content(self, components_quantities, volume=None):
        if volume > 0:
            final_volume = self.content.volume + volume
            if (self.capacity is not None) and (final_volume > self.capacity):
                raise TransferError(
                    "Transfer of %.2e L to %s brings volume over capacity."
                    % (volume, self)
                )
            self.content.volume = final_volume
        for component, quantity in components_quantities.items():
            if component not in self.content.quantities:
                self.content.quantities[component] = 0
            self.content.quantities[component] += quantity


    def subtract_content(self, components_quantities, volume=0):
        if volume > 0:
            if volume > self.volume:
                raise TransferError(
                    ("Substraction of %.2e L from %s impossible."
                     " Current volume: %.2e L")
                    % (volume, self, self.volume)
                )
            self.content.volume -= volume
        for component, quantity in components_quantities.items():
            if self.content.quantities[component] == quantity:
                self.content.quantities.pop(component)
            else:
                self.content.quantities[component] -= quantity
    
    def empty_completely(self):
        self.content.quantities = {}
        self.content.volume = 0

    @property
    def coordinates(self):
        """Return (well.row, well.column)"""
        return (self.row, self.column)

    @property
    def is_empty(self):
        """Return true iff the well's volume is 0"""
        return (self.volume == 0)


    def __repr__(self):
        return "(%s-%s)" % (self.plate.name, self.name)

    def pretty_summary(self):
        data = "\n    ".join([""] + [
            ("%s: %s" % (key, value))
            for key, value in self.data.items()])
        content = "\n    ".join([""] + [
            ("%s: %s" % (key, value))
            for key, value in self.content.quantities.items()])
        return (
            "{self}\n"
            "  Volume: {self.volume}\n"
            "  Content: {content}\n"
            "  Metadata: {data}"
        ).format(self=self, content=content, data=data)

    def to_dict(self):
        return dict(
            [
                ["name", self.name],
                ["content", self.content.to_dict()],
                ["row", self.row],
                ["column", self.column],
            ] + list(self.data.items())
        )

    def index_in_plate(self, direction='row'):
        """Return the index of the well in the plate."""
        return self.plate.wellname_to_index(self.name, direction=direction)
    
    def is_after(self, other, direction='row'):
        """Return whether this well is located strictly after the other well.
        
        Examples
        --------
        To iterate over all free wells after the last non-free well of a plate:

        >>> direction = 'row'
        >>> last_occupied_well = plate.last_nonempty_well(direction=direction)
        >>> free_wells = (w for w in plate.iter_wells(direction=direction)
        >>>               if w.is_after(last_occupied_well))
        >>> for well in free_wells: ...
        """
        well_index = self.index_in_plate(direction=direction)
        other_index = other.index_in_plate(direction=direction)
        return well_index > other_index

    def __lt__(self, other):
        return str(self) < str(other)
