package com.example.bigdata;

import com.espertech.esper.common.client.EPCompiled;
import com.espertech.esper.common.client.EventBean;
import com.espertech.esper.common.client.configuration.Configuration;
import com.espertech.esper.compiler.client.CompilerArguments;
import com.espertech.esper.compiler.client.EPCompileException;
import com.espertech.esper.compiler.client.EPCompiler;
import com.espertech.esper.compiler.client.EPCompilerProvider;
import com.espertech.esper.runtime.client.*;
import net.datafaker.Faker;
import net.datafaker.transformations.JsonTransformer;
import net.datafaker.transformations.Schema;


import java.sql.Timestamp;
import java.time.Instant;
import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;
import java.util.concurrent.TimeUnit;

import static net.datafaker.transformations.Field.field;

public class EsperClient {
    public static void main(String[] args) throws InterruptedException {
        int noOfRecordsPerSec;
        int howLongInSec;
        if (args.length < 2) {
            noOfRecordsPerSec = 100;
            howLongInSec = 15;
        } else {
            noOfRecordsPerSec = Integer.parseInt(args[0]);
            howLongInSec = Integer.parseInt(args[1]);
        }

        Configuration config = new Configuration();
        EPCompiled epCompiled = getEPCompiled(config);

        // Connect to the EPRuntime server and deploy the statement
        EPRuntime runtime = EPRuntimeProvider.getRuntime("http://localhost:port", config);
        EPDeployment deployment;
        try {
            deployment = runtime.getDeploymentService().deploy(epCompiled);
        }
        catch (EPDeployException ex) {
            // handle exception here
            throw new RuntimeException(ex);
        }

        EPStatement resultStatement = runtime.getDeploymentService().getStatement(deployment.getDeploymentId(), "answer");

        // Add a listener to the statement to handle incoming events
        resultStatement.addListener( (newData, oldData, stmt, runTime) -> {
            for (EventBean eventBean : newData) {
                System.out.printf("R: %s%n", eventBean.getUnderlying());
            }
        });

        Faker faker = new Faker();
        String record;

        long startTime = System.currentTimeMillis();
        while (System.currentTimeMillis() < startTime + (1000L * howLongInSec)) {
            for (int i = 0; i < noOfRecordsPerSec; i++) {
                String locations = faker.warhammerFantasy().locations();
                Timestamp eTimestamp = faker.date().past(10, TimeUnit.SECONDS);
                eTimestamp.setNanos(0);
                Timestamp iTimestamp = Timestamp.valueOf(LocalDateTime.now().withNano(0));
                Schema<Object, ?> schema = Schema.of(
                        field("location", () -> locations),
                        field("attack_faction", () -> faker.warhammerFantasy().factions()),
                        field("defend_faction", () -> faker.warhammerFantasy().factions()),
                        field("attack_number_of_units", () -> String.valueOf((faker.number().randomNumber()%50)+1)),
                        field("defend_number_of_units", () -> String.valueOf((faker.number().randomNumber()%50)+1)),
                        field("winner", () -> String.valueOf(faker.number().numberBetween(1,3))),
                        field("ets", eTimestamp::toString),
                        field("its", iTimestamp::toString)
                        );

                JsonTransformer<Object> transformer = JsonTransformer.builder().build();
                record = transformer.generate(schema, 1);
                runtime.getEventService().sendEventJson(record, "WarhammerEvent");
            }
            waitToEpoch();
        }
    }

    private static EPCompiled getEPCompiled(Configuration config) {
        CompilerArguments compilerArgs = new CompilerArguments(config);

        // Compile the EPL statement
        EPCompiler compiler = EPCompilerProvider.getCompiler();
        EPCompiled epCompiled;

        /*
        Zad 1
                    @name('answer') SELECT attack_faction, SUM(attack_number_of_units) as number_of_all_attack_units
                    FROM WarhammerEvent#ext_timed_batch(java.sql.Timestamp.valueOf(its).getTime(), 10 sec)
                    GROUP BY attack_faction
                    ORDER BY SUM(attack_number_of_units) DESC;

        Zad 2
                    @name('answer') SELECT *
                    FROM WarhammerEvent#length(1)
                    WHERE (attack_number_of_units < defend_number_of_units and winner = 1) OR
                    (defend_number_of_units < attack_number_of_units and winner = 2);

        Zad 3
                    @name('answer') SELECT AVG(attack_number_of_units) as avg_atk_unit, attack_faction, attack_number_of_units
                    FROM WarhammerEvent(winner = 1)#ext_timed_batch(java.sql.Timestamp.valueOf(its).getTime(), 10 sec)
                    HAVING attack_number_of_units + 10 <= AVG(attack_number_of_units);

        Zad 4*
                    @name('answer')
                    select
                    (
                    SELECT sum(attack_number_of_units) as suma1
                    FROM WarhammerEvent#length(10)
                    where attack_faction = 'The Empire'
                    ) +
                    (
                    SELECT sum(defend_number_of_units) as suma2
                    FROM WarhammerEvent#length(10)
                    where defend_faction = 'The Empire'
                    ) as units_of_empire,
                    (
                    SELECT sum(attack_number_of_units) as suma3
                    FROM WarhammerEvent#length(10)
                    where attack_faction = 'Beasts of Chaos'
                    ) +
                    (
                    SELECT sum(defend_number_of_units) as suma4
                    FROM WarhammerEvent#length(10)
                    where defend_faction = 'Beasts of Chaos'
                    ) as units_of_beasts
                    from WarhammerEvent

        Zad 5

                    create window WarhammerTicker#length(10) as WarhammerEvent;
                    insert into WarhammerTicker select * from WarhammerEvent;
                    @name('answer')
                    select p[0].ets as ets1, p[1].ets as ets2, p[2].ets as ets3
                    from pattern[every ([3:]
                    p=    WarhammerTicker((attack_faction="The Empire" and winner=1) or (defend_faction="The Empire" and winner=0))
                    until WarhammerTicker((attack_faction="Beasts of Chaos" and winner=1) or (defend_faction="Beasts of Chaos" and winner=0))
                    )]

        Zad 6

                    create window WarhammerTicker#length(10) as WarhammerEvent;
                    insert into WarhammerTicker select * from WarhammerEvent;
                    @name('answer')
                    select e1.ets as ets1, e4.ets as ets4, e1.attack_faction as faction_name
                    from pattern[
                    every e1 = WarhammerTicker() ->
                    e2 = WarhammerTicker(attack_faction=e1.attack_faction) and not WarhammerTicker(defend_faction=e1.attack_faction) ->
                    e3 = WarhammerTicker(defend_faction=e1.attack_faction) and not WarhammerTicker(attack_faction=e1.attack_faction) ->
                    e4 = WarhammerTicker(defend_faction=e1.attack_faction) and not WarhammerTicker(attack_faction=e1.attack_faction)
                    ]

        Zad 7
                    create window WarhammerTicker#length(10) as WarhammerEvent;
                    insert into WarhammerTicker select * from WarhammerEvent;
                    @name('answer')
                    select ets1, ets2, ets3, defend_faction
                    from WarhammerTicker
                    match_recognize (
                        partition by defend_faction
                        measures win.ets as ets1, secondwin.ets as ets2, last(keepwinning.ets) as ets3, win.defend_faction as defend_faction
                        pattern (win secondwin keepwinning+)
                        define
                            win as win.winner = 2,
                            secondwin as secondwin.winner = 2 and secondwin.defend_number_of_units < win.defend_number_of_units,
                            keepwinning as keepwinning.winner = 2 and keepwinning.defend_number_of_units < prev(keepwinning.defend_number_of_units)
                    )
         */


        try {
            epCompiled = compiler.compile("""
                            @public @buseventtype create json schema WarhammerEvent(location string,
                            attack_faction string, defend_faction string, attack_number_of_units int,
                            defend_number_of_units int, winner int, ets string, its string);
                                                                            
                    @name('answer')
                    select
                    (
                    SELECT sum(attack_number_of_units) as suma1
                    FROM WarhammerEvent#length(10)
                    where attack_faction = 'The Empire'
                    ) +
                    (
                    SELECT sum(defend_number_of_units) as suma2
                    FROM WarhammerEvent#length(10)
                    where defend_faction = 'The Empire'
                    ) as units_of_empire,
                    (
                    SELECT sum(attack_number_of_units) as suma3
                    FROM WarhammerEvent#length(10)
                    where attack_faction = 'Beasts of Chaos'
                    ) +
                    (
                    SELECT sum(defend_number_of_units) as suma4
                    FROM WarhammerEvent#length(10)
                    where defend_faction = 'Beasts of Chaos'
                    ) as units_of_beasts
                    from WarhammerEvent
                            """,
                    compilerArgs);
        }
        catch (EPCompileException ex) {
            // handle exception here
            throw new RuntimeException(ex);
        }
        return epCompiled;
    }

    static void waitToEpoch() throws InterruptedException {
        long millis = System.currentTimeMillis();
        Instant instant = Instant.ofEpochMilli(millis) ;
        Instant instantTrunc = instant.truncatedTo( ChronoUnit.SECONDS ) ;
        long millis2 = instantTrunc.toEpochMilli() ;
        TimeUnit.MILLISECONDS.sleep(millis2+1000-millis);
    }
}

