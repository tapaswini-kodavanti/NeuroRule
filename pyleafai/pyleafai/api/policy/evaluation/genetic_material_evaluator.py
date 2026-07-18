
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


class GeneticMaterialEvaluator():
    '''
    An interface that evaluates a piece of GeneticMaterial against a given
    Record describing evaluated data.

    An Evaluator has as its most meaningful class method, a Pure Function
    which evaluates a given piece of GeneticMaterial against a given Record.
    The results of the evaluation are given in the returned EvaluationResults
    object of the evaluate() method.

    Both the input GeneticMaterial and the input Record are expected to be
    read-only, data-only objects with no explicit policy attached to them.
    Evaluation policy (including Record interpretation) emanates from
    derivations from self interface.

    Any given GeneticMaterialEvalautor will be tightly coupled (at least) to
    the class of GeneticMaterial it is evaluating, as well as the base type
    of the EvaluationResults yielded by the evaluation.

    For any given piece of GeneticMaterial, they might be more than one way
    to interpret the data described by it. In such a case, there would be a
    single implementation for each interpretation of the GeneticMaterial data.

    Also, for any given GeneticMaterial interpretation, there might be more
    than one way to perform the evaluation to obtain the same EvaluationResults,
    (e.g. optimized vs. brute force, or GPU vs. CPU). Each of these cases
    might have their own GeneticMaterialEvaluator implementation as well.
    '''

    def evaluate(self, genetic_material, evaluation_data):
        '''
        Evaluate the given GeneticMaterial on the given evaluatedData Record.
        This method is a Pure Function.

        :param genetic_material:
                an unspecified type which can provide access to the
                data-only components of just what is to be evaluated.

                A GeneticMaterial implementation provides no policy methods
                as to specifically how an evaluation of the GM data will take
                place in and of itself. Such policy methods are specifically
                reserved for one or more GeneticMaterialEvaluator classes for
                a specific GM type, which allows for multiple ways to interpret
                the same GM data.

       :param evaluation_data:
                a Record which can completely describe the data against which
                a piece of GeneticMaterial is evaluated.

                It is expected that a single instance of GeneticMaterial will
                be tested against multiple instance of evaluatedData Records
                for the purposes of training of real-life/inference use.

                All interpretations of the evaluatedData Record class are also
                left to implementations, such as data layout and Schema of the
                Record itself, as specific classes/groupings of GeneticMaterial
                might require specific Schema for accessing data.

                Items which might need to appear somewhere as a field (or
                sub-Record field) in an evaluatedData Record could include:
                    a) Data Sample information
                    b) Data View information as to which part of a Data Sample
                        is under scrutiny at the time of evaluation.
                    c) Feedback data for a specific Individual's transient,
                        state which is carried forward for evaluation.

       :return: The results EvaluationResults, which pairs together an
                unspecified type containing the transient Results
                of the evaluation, couple with separate Metrics Record
                measurements describing *how* the evaluate() call
                went, regardless of Results.
        '''

        raise NotImplementedError
