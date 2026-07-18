
# Copyright (C) 2020-2023 Cognizant Digital Business, Evolutionary AI.
# All Rights Reserved.
#
# This software is a trade secret, and contains proprietary and confidential
# materials of Cognizant Digital Business Evolutionary AI.
# Cognizant Digital Business prohibits the use, transmission, copying,
# distribution, or modification of this software outside of the
# Cognizant Digital Business EAI organization.
#
# END COPYRIGHT

from pyleafai.api.data.metrics_provider import MetricsProvider


class Individual(MetricsProvider):
    """
    An Individual is a data-only construct which brings together the other
    data-only constructs of:
    <ul>
      <li>GeneticMaterial</li>
      <li>Metrics</li>
      <li>Identity</li>
    </ul>
    <p>
    Once created, it and all its parts are considered to be immutable.
    <p>
    We expect Individual and its components to be data-only and therefore
    utterly serializable (in the abstract sense).
    """

    def __init__(self, genetic_material, identity, metrics=None):
        """
        Constructs an Individual from some genetic material, and potentially
        some metrics.

        :param genetic_material: the object which makes up the
                genetic material of the Individual
        :param identity: the Identity information for the Individual describing
                the creation circumstances of this Individual.
        :param metrics: the Metrics informat comprised of measurements of the
                 genetic_material against real Data Samples.
        """
        self._genetic_material = genetic_material
        self._metrics = metrics
        self._identity = identity

    def get_genetic_material(self):
        """
        Returns the genetic material of this Individual.
        :return: the root of the GeneticMaterial belonging to the Individual
        """
        return self._genetic_material

    def get_metrics(self):
        """
        Returns the metrics object of this Individual.
        Can return None if the Individual has never been evaluated.

        :return: the Metrics object belonging to the Individual.
        """
        return self._metrics

    def get_identity(self):
        """
        :return: the Identity of the Individual
        """
        return self._identity
