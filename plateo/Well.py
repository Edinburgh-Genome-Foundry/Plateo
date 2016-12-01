
class TransferError(ValueError):
    pass

class Well:
    """Generic class for a well"""
    capacity = None

    def __init__(self, plate, row, column, name, metadata=None):
        self.plate = plate
        self.row = row
        self.column = column
        self.name = name
        self.metadata = {} if metadata is None else metadata
        self.sources = []
        self.content = {}
        self.volume = 0

    def iterate_sources_tree(self):
        for source in self.sources:
            if isinstance(source, Well):
                for parent in source.iterate_sources_tree():
                    yield parent
            else:
                yield source
        yield self

    def transfer_to_other_well(self, destination_well, transfer_volume):
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
                "Transfer of %.2e L to %s brings volume over capacity."
                % (transfer_volume, destination_well)
            )

        #  If you arrive here, it means that the transfer is valid, do it.
        quantities_transfered = {
            component: quantity * factor
            for component, quantity in self.content.items()
        }
        destination_well.add_content(quantities_transfered,
                                     volume=transfer_volume)
        self.subtract_content(quantities_transfered,
                              volume=transfer_volume)
        if self not in destination_well.sources:
            destination_well.sources.append(self)

    def add_content(self, components_quantities, volume=None):
        if volume > 0:
            final_volume = self.volume + volume
            if (self.capacity is not None) and (final_volume > self.capacity):
                raise TransferError(
                    "Transfer of %.2e L to %s brings volume over capacity."
                    % (volume, self)
                )
            self.volume = final_volume
        for component, quantity in components_quantities.items():
            if component not in self.content:
                self.content[component] = 0
            self.content[component] += quantity


    def subtract_content(self, components_quantities, volume=0):
        if volume > 0:
            if volume > self.volume:
                raise TransferError(
                    ("Substraction of %.2e L from %s impossible."
                     " Current volume: %.2e L")
                    % (volume, self, self.volume)
                )
            self.volume -= volume
        for component, quantity in components_quantities.items():
            self.content[component] -= quantity

    @property
    def coordinates(self):
        return (self.row, self.column)

    @property
    def is_empty(self):
        return (self.volume == 0)


    def __repr__(self):
        return "(%s-%s)" % (self.plate.name, self.name)

    def pretty_summary(self):
        metadata = "\n    ".join([""] + [("%s: %s" % (key, value))
                                         for key, value in self.metadata.items()])
        content = "\n    ".join([""] + [("%s: %s" % (key, value))
                                        for key, value in self.content.items()])
        return (
            "{self}\n"
            "  Volume: {self.volume}\n"
            "  Content: {content}\n"
            "  Metadata: {metadata}"
        ).format(self=self, content=content, metadata=metadata)

    def to_dict(self):
        return dict(
            [
                ["name", self.name],
                ["content", self.content],
                ["volume", self.volume],
                ["row", self.row],
                ["column", self.column],
            ] + list(self.metadata.items())
        )
