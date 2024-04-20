import java.io.BufferedReader;
import java.io.FileReader;
import java.util.Vector;

import weka.classifiers.AbstractClassifier;
import weka.classifiers.Classifier;
import weka.classifiers.Evaluation;
import weka.core.Instances;
import weka.core.OptionHandler;
import weka.core.Utils;

class TestRegresji
{
	public static void printStats(String dataset, Classifier classifier, Evaluation evaluation)
	{
		StringBuffer result;

		result = new StringBuffer();
		result.append("Dataset	 : " + dataset + "\n");
		result.append("Classifier: " + Utils.toCommandLine(classifier) + "\n\n");

		result.append("Dataset	 : " + dataset + "\n");
		result.append("classifier.toString():\n" + classifier.toString() + "\n");
		result.append("evaluation.toSummaryString():\n" + evaluation.toSummaryString() + "\n");
 
		try {
			result.append("evaluation.toMatrixString():\n" + evaluation.toMatrixString() + "\n");
		} catch (Exception e) {
			e.printStackTrace();
		}

		try {
			result.append("evaluation.toClassDetailsString():\n" + evaluation.toClassDetailsString() + "\n");
		} catch (Exception e) {
			e.printStackTrace();
		}

		System.out.println(result.toString());
	}


	public static void main(String[] args) throws Exception
	{
		String classifierName = "M5P"; //weka.classifiers.trees.M5P; but AbstractClassifier.forName() will find it for us
		String dataset = "regr.arff"; //set your own file name
		//classifierOptions.add(""); //you can add options here (separate add() calls for parameter names and their values)

        Instances instances = new Instances(new BufferedReader(new FileReader(dataset)));
        instances.setClassIndex(instances.numAttributes() - 1);
		// 10-fold CV with seed=1

        for (int i = 0; i < 100; ++i)
        {
            Vector<String> classifierOptions = new Vector<String> ();
            classifierOptions.add("-M");
            classifierOptions.add(String.valueOf(i));

            Classifier classifier = AbstractClassifier.forName(classifierName, classifierOptions.toArray(new String[classifierOptions.size()]));
            classifier.buildClassifier(instances); //use this line to build the classifier on the entire set (and display it later in printStats())

            Evaluation evaluation = new Evaluation(instances);
            evaluation.crossValidateModel(classifier, instances, 10, instances.getRandomNumberGenerator(1));

            // printStats(dataset, classifier, evaluation);
            System.out.println(evaluation.meanAbsoluteError() + ",");
        }
	}

};