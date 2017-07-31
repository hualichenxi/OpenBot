import com.google.gson.*;
import org.apache.jena.query.Dataset;
import org.apache.jena.query.ReadWrite;
import org.apache.jena.rdf.model.*;
import org.apache.jena.tdb.TDBFactory;
import sun.reflect.annotation.ExceptionProxy;

import java.io.BufferedReader;
import java.io.FileOutputStream;
import java.io.FileReader;
import java.net.URLDecoder;
import java.util.HashMap;
import java.util.Map;

public class Transform {
    public static void main(String[] args) {
        try {
//            String assemble_file = "output/tdb-assemler.ttl";
//            Dataset dataset = TDBFactory.assembleDataset(assemble_file);
//            dataset.begin(ReadWrite.WRITE);
            process_entity();
            process_cvt();
//            dataset.end();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public static void process_cvt() throws Exception {
        String basic_url = "http://cvt.baike.com/";
        String people_filename = "cvt.json";
        FileReader reader = new FileReader(people_filename);
        BufferedReader br = new BufferedReader(reader);
        String str = null; Model model = ModelFactory.createDefaultModel();
        Map<String, Property> prop_map = new HashMap<String, Property>();
        Property prop_id = model.createProperty("id");
        Property prop_work = model.createProperty("work");
        Property prop_role = model.createProperty("role");
        Property prop_actor = model.createProperty("actor");


        JsonParser parser = new JsonParser();
        while ((str = br.readLine()) != null) {
            JsonObject obj = parser.parse(str).getAsJsonObject();
            String iid = obj.getAsJsonPrimitive("id").getAsString();
            String url = basic_url + iid;

            Resource res = model.createResource(url).addProperty(prop_id, iid);

            JsonObject info_obj = obj.getAsJsonObject("relation");
            if (obj.get("relation") == null || !obj.get("relation").isJsonObject()) {
                continue;
            } else {
                JsonObject relation_obj = obj.getAsJsonObject("relation");
                String work = relation_obj.getAsJsonPrimitive("work").getAsString();
                String role = relation_obj.getAsJsonPrimitive("role").getAsString();
                String actor = relation_obj.getAsJsonPrimitive("actor").getAsString();
                res.addProperty(prop_work, work);
                res.addProperty(prop_role, role);
                res.addProperty(prop_actor, actor);
            }
        }

        br.close();
        reader.close();
        model.write(new FileOutputStream("cvt.ttl"), "Turtle");
    }

    public static void process_entity() throws Exception {
        String basic_url = "http://entity.baike.com/";
        String people_filename = "entity.json";
        FileReader reader = new FileReader(people_filename);
        BufferedReader br = new BufferedReader(reader);
        String str = null;

        Model model = ModelFactory.createDefaultModel();
        Map<String, Property> prop_map = new HashMap<String, Property>();
        Property prop_title = model.createProperty("title");
        Property prop_type = model.createProperty("type");
        Property prop_id = model.createProperty("id");


        JsonParser parser = new JsonParser();
        while ((str = br.readLine()) != null) {
            JsonObject obj = parser.parse(str).getAsJsonObject();
            String title = obj.getAsJsonPrimitive("title").getAsString();
            String typ = obj.getAsJsonPrimitive("type").getAsString();
            String iid = obj.getAsJsonPrimitive("id").getAsString();
            String url = basic_url + iid;

            Resource res = model.createResource(url).addProperty(prop_title, title)
                .addProperty(prop_type, typ).addProperty(prop_id, iid);

            JsonObject info_obj = obj.getAsJsonObject("infobox");
            if (obj.get("infobox") == null || !obj.get("infobox").isJsonObject()) {
                continue;
            } else {
                for (Map.Entry<String, JsonElement> entry : info_obj.entrySet()) {
                    try {
                        String key = entry.getKey();
                        String value = entry.getValue().toString();

                        if (!prop_map.containsKey(key)) {
                            prop_map.put(key, model.createProperty(key));
                        }
                        Property prop = prop_map.get(key);
                        res.addProperty(prop, value);
                    } catch (Exception e) {

                    }

                }
            }
        }

        br.close();
        reader.close();
        model.write(new FileOutputStream("entity.ttl"), "Turtle");
    }
}