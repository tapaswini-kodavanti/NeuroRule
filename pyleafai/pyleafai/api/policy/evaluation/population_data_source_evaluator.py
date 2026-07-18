
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


class PopulationDataSourceEvaluator():
    """
    An interface that evaluates objects (whose type is left as an
    implementation detail) on a Source (potentially streamed sequence)
    of Data Samples and returns Metrics Record/dictionary measurements for
    each evaluated object in the form of a Map.

    Using the Map as a return type allows for:

      a) Specific Metrics Records to be associated with the object whose
        evaluation generated them.
      b) the possibility that not all evaluations will be able to complete.
    """

    def evaluate_population_on_source(self, population, data_sample):
        """
        Evaluates a collection of objects on some data.

        If a single PopulationDataSourceEvaluator implementation is to evaluate
        heterogeneously configured populations, the configuration of each
        member of the population is left as an implementation detail.

        :param population:
                   the immutable collection of objects to evaluate on the same
                   Data Sample Record

        :param data_sample:
                    a potentially streamed Source for a single read-only Record
                    comprising a single Data Sample, against which all the
                    members of the population are evaluated

        :return: a Map/dictionary where the key is a population member object,
                and the corresponding value a metrics Record which describes
                measurements taken during the course of evaluate() for this
                object
        """
        raise NotImplementedError
