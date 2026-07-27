import "./GlowButton.css";

export default function GlowButton({

    children,

    onClick

}){

    return(

        <button

            className="glow-button"

            onClick={onClick}

        >

            {children}

        </button>

    );

}