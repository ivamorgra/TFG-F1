from pyparsing import col
from pyspark.sql import SparkSession
from pyspark.ml.classification import LogisticRegression
from pyspark.ml.evaluation import BinaryClassificationEvaluator, RegressionEvaluator
from pyspark.ml.classification import LogisticRegressionModel
from pyspark.ml.feature import VectorAssembler

def train_model():
    spark = SparkSession.builder.getOrCreate()

    # Carga el CSV de resultados
    results_df = spark.read.csv('./data/results_data.csv', header=True, inferSchema=True).select("driverId", "constructorId", "points","position")

    # Carga el CSV de pilotos
    drivers_df = spark.read.csv('./datasets/drivers.csv', header=True, inferSchema=True).select("driverId","forename","surname")


    merged_df = results_df.join(drivers_df, "driverId", "inner")

    # Proporción de datos
    train_ratio = 0.7  # Proporción para entrenamiento (70%)
    test_ratio = 0.3  # Proporción para prueba (30%)

    # Divide el DataFrame en conjuntos de entrenamiento y prueba
    train_data, test_data = merged_df.randomSplit([train_ratio, test_ratio], seed=42)




    # Creación de una instancia del modelo de regresión logística
    lr = LogisticRegression(featuresCol='features', labelCol='position')


    # Seleccionar las columnas relevantes para las características (features)
    selected_columns = ["driverId", "constructorId", "points","position"]
    assembler = VectorAssembler(inputCols=selected_columns, outputCol="features")
    # Transformar los datos de entrenamiento utilizando el ensamblador
    training_data = assembler.transform(train_data)
    training_data.show()

    # Ajustar el modelo de regresión logística utilizando los datos de entrenamiento
    lr_model = lr.fit(training_data)




    # Hacer predicciones en el conjunto de prueba utilizando el modelo entrenado
    validation_data = assembler.transform(test_data)
    predictions = lr_model.transform(validation_data)

    predictions.show()
    # Calcular métricas de evaluación para el problema de clasificación o regresión
    if lr.getFamily() == "binomial":
        evaluator = BinaryClassificationEvaluator(labelCol='position')
        accuracy = evaluator.evaluate(predictions)
        print(f"Accuracy: {accuracy}")
    else:
        evaluator = RegressionEvaluator(labelCol='position', metricName='rmse')
        rmse = evaluator.evaluate(predictions)
        print(f"RMSE: {rmse}")


    return predictions