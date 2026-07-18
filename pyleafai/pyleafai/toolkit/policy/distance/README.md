
Distance function implementation that satisfy basic distance
measurements for dictionaries and lists.  This notion is
extensible.

If you are looking at the code for the first time, it helps
to have the dependencies outlined:

NormalizedDictionaryDistance
+ FlattenedDictionaryDistance
  + DictionaryLeafCountDistance
    + LeafCountDistanceRegistry
      + DistanceRegistry
      + ConstantDistance
      + ListLeafCountDistance
  + FlattenedBranchDistanceRegistry
    + DistanceRegistry
    + FlattenedListDistance
    + NormalizedNumberDistance
    + AllOrNothingDistance
