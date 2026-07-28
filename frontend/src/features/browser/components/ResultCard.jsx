export default function ResultCard(){

    return(

        <div
            style={{
                padding:"20px",
                borderRadius:"18px",
                marginBottom:"20px",

                background:"rgba(255,255,255,.05)",

                border:"1px solid rgba(255,255,255,.08)"
            }}
        >

            <h3
                style={{
                    color:"#35F6FF",
                    marginBottom:"10px"
                }}
            >
                Search Result
            </h3>

            <p
                style={{
                    color:"#CBD5E1",
                    lineHeight:1.7
                }}
            >
                AI generated search results will appear here.
            </p>

        </div>

    );

}