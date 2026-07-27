import "./TopStatusBar.css";

export default function TopStatusBar() {

    return (

        <header className="topbar">

            <div className="logo">

                ⚡ ASTRA

            </div>

            <div className="status">

                <div className="chip">

                    CPU 14%

                </div>

                <div className="chip">

                    RAM 42%

                </div>

                <div className="chip">

                    GPU 5%

                </div>

                <div className="chip online">

                    ● ONLINE

                </div>

                <div className="chip">

                    02:58 AM

                </div>

            </div>

        </header>

    );

}