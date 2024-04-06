package com.example.bigdata;

import com.espertech.esper.common.client.EPCompiled;
import com.espertech.esper.common.client.EventBean;
import com.espertech.esper.common.client.configuration.Configuration;
import com.espertech.esper.compiler.client.CompilerArguments;
import com.espertech.esper.compiler.client.EPCompileException;
import com.espertech.esper.compiler.client.EPCompiler;
import com.espertech.esper.compiler.client.EPCompilerProvider;
import com.espertech.esper.runtime.client.*;

public class EsperClient {

    public static void main(String[] args) {

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
        // String processing and making JsonObject out of it
        resultStatement.addListener( (newData, oldData, stmt, runTime) -> {
            for (EventBean eventBean : newData) {
                System.out.println(eventBean.getUnderlying());
            }
        });

        for (String s : createInputData()) {
            runtime.getEventService().sendEventJson(s, "Ticker");
        }
    }

    private static EPCompiled getEPCompiled(Configuration config) {
        CompilerArguments compilerArgs = new CompilerArguments(config);

        // Compile the EPL statement
        EPCompiler compiler = EPCompilerProvider.getCompiler();
        EPCompiled epCompiled;
        try {
            epCompiled = compiler.compile("""
                    @public @buseventtype create json schema Ticker(symbol string, name string);
                    create window AcmeTicker#length(10) as Ticker;
                    insert into AcmeTicker select * from Ticker;
                    @name('answer')
                    select a.symbol, b.symbol from pattern[ every a=AcmeTicker(name="A") -> every b=AcmeTicker(name="B")]
                    """, compilerArgs);
        }
        catch (EPCompileException ex) {
            // handle exception here
            throw new RuntimeException(ex);
        }
        return epCompiled;
    }

    static String[] createInputData() {
        return new String[] {
                "{\"symbol\":\"A1\", \"name\":\"A\"}",
                "{\"symbol\":\"B1\", \"name\":\"B\"}",
                "{\"symbol\":\"C1\", \"name\":\"C\"}",
                "{\"symbol\":\"B2\", \"name\":\"B\"}",
                "{\"symbol\":\"A2\", \"name\":\"A\"}",
                "{\"symbol\":\"D1\", \"name\":\"D\"}",
                "{\"symbol\":\"A3\", \"name\":\"A\"}",
                "{\"symbol\":\"B3\", \"name\":\"B\"}",
                "{\"symbol\":\"E1\", \"name\":\"E\"}",
                "{\"symbol\":\"A4\", \"name\":\"A\"}",
                "{\"symbol\":\"F1\", \"name\":\"F\"}",
                "{\"symbol\":\"B4\", \"name\":\"B\"}"
        };
    }
}

