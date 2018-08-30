$(function (){

  var intervalo = setInterval(function (){
    clearInterval(intervalo);

    document.getElementById("carregando").style.display = "none";
    document.getElementById("corpo").style.display = "block";
  },500);
});

function clickLoad(){
  document.getElementById("corpo").style.display = "none";
  document.getElementById("carregando").style.display = "block";
}

function imprimir(){
  alert('Seu arquivo será preparado em nova aba!');
}

function redireciona(){
  alert('Você será direcionado para o site www.cvedetails.com');
}

function checkAll(o){
	var boxes = document.getElementsByTagName("input");
	for (var x=0;x<boxes.length;x++){
		var obj = boxes[x];
		if (obj.type == "checkbox"){
			if (obj.name!="chkAll") obj.checked = o.checked;
		}
	}
}

// criei uma função css que deixa sempre a tela de load e esconte o conteudo da pagina.
// criei função javaScript que retira essa tela e carrega o conteúdo.
// criei uma outra função para que a cada click seja carregada a tela de laod;
