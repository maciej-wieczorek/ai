# BigData Projekt 2

## Producent; skrypty inicjujące i zasilający


### Klaster
```
gcloud dataproc clusters create ${CLUSTER_NAME} \
--enable-component-gateway --region ${REGION} --subnet default \
--master-machine-type n1-standard-4 --master-boot-disk-size 50 \
--num-workers 2 --worker-machine-type n1-standard-2 --worker-boot-disk-size 50 \
--image-version 2.1-debian11 --optional-components JUPYTER,ZOOKEEPER,DOCKER \
--project ${PROJECT_ID} --max-age=3h \
--metadata "run-on-master=true" \
--initialization-actions \
gs://goog-dataproc-initialization-actions-${REGION}/kafka/kafka.sh
```

### Skryp tworzący źródłowe tematy Kafki i resetujący środowisko
```
kafka_init_reset.sh
```

### Skrypt zasilający tematy Kafki
```
kafka_suppy.sh
```

## Utrzymanie obrazu czasu rzeczywistego – transformacje

## Utrzymanie obrazu czasu rzeczywistego – obsługa trybu A

## Utrzymanie obrazu czasu rzeczywistego – obsługa trybu C

## Wykrywanie anomalii

## Program przetwarzający strumienie danych; skrypt uruchamiający

## Miejsce utrzymywania obrazów czasu rzeczywistego – skrypt tworzący

## Miejsce utrzymywania obrazów czasu rzeczywistego – cechy

## Konsument: skrypt odczytujący wyniki przetwarzania