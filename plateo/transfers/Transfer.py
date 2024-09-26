class Transfer:
    """A tranfer from a source to a destination

    Parameters
    ----------

    source_well
      A Well object representing the plate well from which to transfer

    destination_well
      A Well object representing the plate well to which to transfer.

    volume
      Volume to be transfered, expressed in liters.

    data
      A dict containing any useful information on the transfer, this
      information can be used later e.g. as parameters for the transfer
      when exporting a picklist.
    """

    def __init__(self, source_well, destination_well, volume, data=None):

        self.volume = volume
        self.source_well = source_well
        self.destination_well = destination_well
        self.data = data

    def to_plain_string(self):
        """Return "xx L from {source_well} into {dest_well}"."""
        return (
            "{self.volume:.02E}L from {self.source_well.plate.name} "
            "{self.source_well.name} into "
            "{self.destination_well.plate.name} "
            "{self.destination_well.name}"
        ).format(self=self)

    def change_volume(self, new_volume):
        """Return a version of the transfer with a new volume."""
        return Transfer(
            source_well=self.source_well,
            destination_well=self.destination_well,
            volume=new_volume,
            data=self.data,
        )

    def __repr__(self):
        """Return "xx L from {source_well} into {dest_well}"."""
        return self.to_plain_string()
